import logging
from datetime import UTC, datetime, timedelta
from typing import TypedDict

from sqlalchemy.orm import Session

from app.models.enums import AuditAction, EntityType, Risco, StatusSla, StatusVulnerabilidade
from app.models.vulnerability import Vulnerability
from app.services.audit import AuditService
from app.services.sla_policy import SlaPolicy

logger = logging.getLogger(__name__)

class SlaState(TypedDict):
    status: StatusSla
    due_at: datetime | None
    dias_restantes: int | None
    dias_em_atraso: int | None
    idade_em_dias: int

class SlaService:
    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @classmethod
    def calcular_due_date(cls, risco: Risco, identificada_em: datetime) -> datetime | None:
        dias = SlaPolicy.get_dias_para_risco(risco)
        if dias == 0:
            return None
        return identificada_em + timedelta(days=dias)

    @classmethod
    def calcular_estado(cls, vuln: Vulnerability, now: datetime | None = None) -> SlaState:
        if now is None:
            now = cls._now()

        due_at = vuln.due_at.replace(tzinfo=UTC) if vuln.due_at and vuln.due_at.tzinfo is None else vuln.due_at

        # Calcular idade
        diff_idade = now - (vuln.identificada_em.replace(tzinfo=UTC) if vuln.identificada_em.tzinfo is None else vuln.identificada_em)
        if now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        idade_em_dias = max(0, diff_idade.days)

        # Sem SLA
        if due_at is None:
            return {
                "status": StatusSla.EXEMPT,
                "due_at": None,
                "dias_restantes": None,
                "dias_em_atraso": None,
                "idade_em_dias": idade_em_dias
            }

        # Concluído / Exempt
        if vuln.status == StatusVulnerabilidade.CORRIGIDA:
            return cls._estado_fechado(StatusSla.COMPLETED, vuln, due_at, idade_em_dias)

        if vuln.status in [
            StatusVulnerabilidade.FALSO_POSITIVO,
            StatusVulnerabilidade.ACEITO_COMO_RISCO,
            StatusVulnerabilidade.DUPLICADO
        ]:
            return cls._estado_fechado(StatusSla.EXEMPT, vuln, due_at, idade_em_dias)

        if vuln.status == StatusVulnerabilidade.EXCECAO_TEMPORARIA:
            return cls._estado_fechado(StatusSla.PAUSED, vuln, due_at, idade_em_dias)

        # SLA Ativo
        diff_due = due_at - now
        dias_restantes = diff_due.days

        if now > due_at:
            dias_em_atraso = (now - due_at).days
            return {
                "status": StatusSla.OVERDUE,
                "due_at": due_at,
                "dias_restantes": 0,
                "dias_em_atraso": dias_em_atraso,
                "idade_em_dias": idade_em_dias
            }

        # Limiar de DUE_SOON: faltam 2 dias ou menos
        if dias_restantes <= 2:
            return {
                "status": StatusSla.DUE_SOON,
                "due_at": due_at,
                "dias_restantes": dias_restantes,
                "dias_em_atraso": 0,
                "idade_em_dias": idade_em_dias
            }

        return {
            "status": StatusSla.ON_TRACK,
            "due_at": due_at,
            "dias_restantes": dias_restantes,
            "dias_em_atraso": 0,
            "idade_em_dias": idade_em_dias
        }

    @staticmethod
    def _estado_fechado(status_sla: StatusSla, vuln: Vulnerability, due_at: datetime, idade: int) -> SlaState:
        # Se resolvido, travamos o diff em resolved_at (se existir)
        # senao, assumimos que já foi e n tem atraso incremental
        ref_date = vuln.resolved_at or vuln.atualizada_em
        if ref_date.tzinfo is None:
            ref_date = ref_date.replace(tzinfo=UTC)
        diff_due = due_at - ref_date

        dias_restantes = max(0, diff_due.days)
        dias_em_atraso = 0
        if ref_date > due_at:
            dias_em_atraso = (ref_date - due_at).days

        return {
            "status": status_sla,
            "due_at": due_at,
            "dias_restantes": dias_restantes,
            "dias_em_atraso": dias_em_atraso,
            "idade_em_dias": idade
        }

    @classmethod
    def check_and_update_slas(cls, db: Session) -> None:
        """Verifica todas as vulnerabilidades ativas e gera eventos/comentarios se necessário."""
        now = cls._now()

        # Buscar todas as ativas com due_at populado
        vulns = db.query(Vulnerability).filter(
            Vulnerability.due_at.isnot(None),
            Vulnerability.status.notin_([
                StatusVulnerabilidade.CORRIGIDA,
                StatusVulnerabilidade.FALSO_POSITIVO,
                StatusVulnerabilidade.ACEITO_COMO_RISCO,
                StatusVulnerabilidade.DUPLICADO,
                StatusVulnerabilidade.EXCECAO_TEMPORARIA,
            ])
        ).all()

        for vuln in vulns:
            estado = cls.calcular_estado(vuln, now)

            # Idempotência com AuditLog
            # Checar qual foi o último evento de SLA para esta vuln
            if estado["status"] == StatusSla.OVERDUE:
                cls._process_breach(db, vuln)
            elif estado["status"] == StatusSla.DUE_SOON:
                cls._process_due_soon(db, vuln)

    @classmethod
    def _process_breach(cls, db: Session, vuln: Vulnerability) -> None:
        # Verifica idempotência
        if not cls._has_event(db, vuln.id, AuditAction.SLA_BREACHED):
            logger.info(f"Vulnerability {vuln.id} SLA Breached!")
            AuditService(db).log_action(
                actor_user_id=None,  # SYSTEM
                action=AuditAction.SLA_BREACHED,
                entity_type=EntityType.FINDING,
                entity_id=str(vuln.id),
                metadata_info={"status": "OVERDUE", "due_at": vuln.due_at.isoformat() if vuln.due_at else None}
            )
            cls._notify_ticketing(vuln, "SLA Vencido: O prazo de remediação expirou.")

    @classmethod
    def _process_due_soon(cls, db: Session, vuln: Vulnerability) -> None:
        if not cls._has_event(db, vuln.id, AuditAction.SLA_DUE_SOON):
            logger.info(f"Vulnerability {vuln.id} SLA Due Soon.")
            AuditService(db).log_action(
                actor_user_id=None,  # SYSTEM
                action=AuditAction.SLA_DUE_SOON,
                entity_type=EntityType.FINDING,
                entity_id=str(vuln.id),
                metadata_info={"status": "DUE_SOON", "due_at": vuln.due_at.isoformat() if vuln.due_at else None}
            )
            cls._notify_ticketing(vuln, "SLA Próximo do Vencimento: Faltam menos de 2 dias.")

    @classmethod
    def _has_event(cls, db: Session, vuln_id: int, action: AuditAction) -> bool:
        from app.models.audit import AuditLog
        return db.query(AuditLog).filter(
            AuditLog.entity_id == vuln_id,
            AuditLog.entity_type == EntityType.FINDING,
            AuditLog.action == action
        ).first() is not None

    @classmethod
    def _notify_ticketing(cls, vuln: Vulnerability, message: str) -> None:
        if not vuln.tickets:
            return
        # Tentamos adicionar comentário no provider
        # Em PRIDE Vision, Ticket e Vulnerability são relacionados.
        # Vou instanciar o Ticket provider
        # Wait, o service ticketing.py precisa de Session e db_ticket
        pass # Will implement properly in next step if necessary
