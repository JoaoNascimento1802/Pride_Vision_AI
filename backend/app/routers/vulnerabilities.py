"""
vulnerabilities.py — Listagem, detalhes e acompanhamento da correção.

Centralizar os achados numa única tela e acompanhar o ciclo de tratamento são
dois dos quatro pilares de ASPM da especificação.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.dependencies import RequirePermission, usuario_atual
from app.database import get_db
from app.models import (
    Application,
    Risco,
    StatusHistory,
    StatusVulnerabilidade,
    User,
    Vulnerability,
)
from app.models.enums import AuditAction, EntityType
from app.models.remediation import RemediationComment, RemediationEvidence
from app.schemas.remediation import CommentCreate, CommentResponse, EvidenceCreate, EvidenceResponse
from app.schemas.ticket import TicketResumo
from app.schemas.vulnerability import (
    AchadoResponse,
    AnaliseIAResponse,
    AtribuicaoRequest,
    HistoricoItem,
    MudancaStatusRequest,
    SlaResponse,
    VulnerabilidadeDetalhe,
    VulnerabilidadeListItem,
)
from app.services.ai_service import ErroProvedorIA, IANaoConfiguradaError, gerar_analise
from app.services.audit import AuditService, get_audit_service
from app.services.sla_service import SlaService
from app.services.state_machine import validar_transicao

router = APIRouter(
    prefix="/api/vulnerabilidades",
    tags=["Vulnerabilidades"],
    dependencies=[Depends(usuario_atual)],
)

# A ordem em que o risco aparece na tela. CASE no SQL em vez de ordenar em
# Python, para a ordenação continuar correta quando houver paginação.
_ORDEM_RISCO = {Risco.CRITICO: 0, Risco.ALTO: 1, Risco.MEDIO: 2, Risco.BAIXO: 3}


def _buscar_ou_404(db: Session, vulnerabilidade_id: int) -> Vulnerability:
    vulnerabilidade = db.get(Vulnerability, vulnerabilidade_id)
    if vulnerabilidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerabilidade não encontrada."
        )
    return vulnerabilidade


def _para_item(vulnerabilidade: Vulnerability, aplicacao: Application) -> VulnerabilidadeListItem:
    item = VulnerabilidadeListItem.model_validate(vulnerabilidade)
    item.aplicacao_nome = aplicacao.nome
    item.aplicacao_ambiente = aplicacao.ambiente.label
    item.tem_analise_ia = vulnerabilidade.tem_analise_ia

    estado_sla = SlaService.calcular_estado(vulnerabilidade)
    item.sla = SlaResponse(
        status=estado_sla["status"].value,
        status_label=estado_sla["status"].label,
        due_at=estado_sla["due_at"],
        dias_restantes=estado_sla["dias_restantes"],
        dias_em_atraso=estado_sla["dias_em_atraso"],
        idade_em_dias=estado_sla["idade_em_dias"]
    )

    return item


@router.get("", response_model=list[VulnerabilidadeListItem])
def listar(
    db: Session = Depends(get_db),
    aplicacao_id: int | None = Query(default=None, description="Filtrar por aplicação"),
    risco: Risco | None = Query(default=None, description="Filtrar por nível de risco"),
    status_filtro: StatusVulnerabilidade | None = Query(
        default=None, alias="status", description="Filtrar por status de correção"
    ),
    tipo_vuln: str | None = Query(default=None, description="Filtrar por tipo"),
    apenas_correlacionadas: bool = Query(
        default=False, description="Somente as confirmadas pelas duas ferramentas"
    ),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> list[VulnerabilidadeListItem]:
    """
    Lista as vulnerabilidades, das mais graves para as menos graves.
    """
    consulta = (
        select(Vulnerability, Application)
        .join(Application, Vulnerability.aplicacao_id == Application.id)
        .options(selectinload(Vulnerability.achados))
    )

    if aplicacao_id is not None:
        consulta = consulta.where(Vulnerability.aplicacao_id == aplicacao_id)
    if risco is not None:
        consulta = consulta.where(Vulnerability.risco == risco)
    if status_filtro is not None:
        consulta = consulta.where(Vulnerability.status == status_filtro)
    if tipo_vuln:
        consulta = consulta.where(Vulnerability.tipo_vuln == tipo_vuln)
    if apenas_correlacionadas:
        consulta = consulta.where(Vulnerability.correlacionada.is_(True))

    linhas = db.execute(consulta).all()

    itens = [_para_item(v, a) for v, a in linhas]
    itens.sort(
        key=lambda i: (
            _ORDEM_RISCO[i.risco],
            not i.correlacionada,
            -i.identificada_em.timestamp(),
        )
    )
    return itens


@router.get("/{vulnerabilidade_id}", response_model=VulnerabilidadeDetalhe)
def detalhar(
    vulnerabilidade_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> VulnerabilidadeDetalhe:
    """
    Detalhes completos: o que cada ferramenta reportou, por que aquele risco foi
    atribuído, o que a IA explicou e todo o histórico de acompanhamento.
    """
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    aplicacao = db.get(Application, vulnerabilidade.aplicacao_id)
    assert aplicacao is not None  # garantido pela chave estrangeira

    base = _para_item(vulnerabilidade, aplicacao)

    analise = None
    if vulnerabilidade.tem_analise_ia:
        analise = AnaliseIAResponse(
            explicacao=vulnerabilidade.ia_explicacao,
            impacto=vulnerabilidade.ia_impacto,
            priorizacao=vulnerabilidade.ia_priorizacao,
            sugestao=vulnerabilidade.ia_sugestao,
            validacao=vulnerabilidade.ia_validacao,
            descricao_ticket=vulnerabilidade.ia_descricao_ticket,
            gerada_em=vulnerabilidade.ia_gerada_em,
        )

    historico = []
    for registro in vulnerabilidade.historico:
        item = HistoricoItem.model_validate(registro)
        item.usuario_nome = registro.usuario.nome if registro.usuario else None
        historico.append(item)

    return VulnerabilidadeDetalhe(
        **base.model_dump(exclude={"risco_label", "status_label", "origens"}),
        justificativa=vulnerabilidade.justificativa,
        atualizada_em=vulnerabilidade.atualizada_em,
        achados=[AchadoResponse.model_validate(a) for a in vulnerabilidade.achados],
        analise_ia=analise,
        historico=historico,
        tickets=[TicketResumo.model_validate(t) for t in vulnerabilidade.tickets],
        owner_id=vulnerabilidade.owner_id,
        owner_team=vulnerabilidade.owner_team,
        assigned_at=vulnerabilidade.assigned_at,
        due_at=vulnerabilidade.due_at,
        resolved_at=vulnerabilidade.resolved_at,
        false_positive_reason=vulnerabilidade.false_positive_reason,
        risk_acceptance_reason=vulnerabilidade.risk_acceptance_reason,
        risk_acceptance_approver_id=vulnerabilidade.risk_acceptance_approver_id,
        risk_accepted_at=vulnerabilidade.risk_accepted_at,
        comments=[CommentResponse.model_validate(c) for c in vulnerabilidade.comments] if hasattr(vulnerabilidade, "comments") else [],
        evidences=[EvidenceResponse.model_validate(e) for e in vulnerabilidade.evidences] if hasattr(vulnerabilidade, "evidences") else [],
    )


@router.patch("/{vulnerabilidade_id}/status", response_model=VulnerabilidadeDetalhe)
def mudar_status(
    vulnerabilidade_id: int,
    dados: MudancaStatusRequest,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service),
) -> VulnerabilidadeDetalhe:
    """
    Altera o status de acompanhamento e registra quem mudou.
    """
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)

    if vulnerabilidade.status is dados.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A vulnerabilidade já está com o status '{dados.status.label}'.",
        )

    try:
        validar_transicao(vulnerabilidade.status, dados.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    from app.auth.rbac import get_permissions
    perms = get_permissions(usuario.role)

    if dados.status.encerrada:
        from app.auth.rbac import get_permissions

        if "finding:close" not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para encerrar (fechar) vulnerabilidades.",
            )

    if dados.status.exige_reason and not dados.reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"O status {dados.status.label} exige uma justificativa (reason).",
        )

    anterior = vulnerabilidade.status
    vulnerabilidade.status = dados.status

    if dados.status == StatusVulnerabilidade.FALSO_POSITIVO:
        vulnerabilidade.false_positive_reason = dados.reason
    elif dados.status == StatusVulnerabilidade.ACEITO_COMO_RISCO:
        vulnerabilidade.risk_acceptance_reason = dados.reason
        vulnerabilidade.risk_acceptance_approver_id = usuario.id
        vulnerabilidade.risk_accepted_at = datetime.now(UTC)
    elif dados.status == StatusVulnerabilidade.CORRIGIDA:
        vulnerabilidade.resolved_at = datetime.now(UTC)

    if anterior == StatusVulnerabilidade.CORRIGIDA and dados.status != StatusVulnerabilidade.CORRIGIDA:
        vulnerabilidade.resolved_at = None

    db.add(
        StatusHistory(
            vulnerabilidade_id=vulnerabilidade.id,
            status_anterior=anterior,
            status_novo=dados.status,
            usuario_id=usuario.id,
            comentario=dados.comentario,
        )
    )

    metadata = {}
    if dados.comentario:
        metadata["comentario"] = dados.comentario
    if dados.reason:
        metadata["reason"] = dados.reason

    audit_action = AuditAction.STATUS_CHANGED
    if dados.status == StatusVulnerabilidade.FALSO_POSITIVO:
        audit_action = AuditAction.FALSE_POSITIVE_MARKED
    elif dados.status == StatusVulnerabilidade.ACEITO_COMO_RISCO:
        audit_action = AuditAction.RISK_ACCEPTED

    audit.log_action(
        action=audit_action,
        actor_user_id=usuario.id,
        entity_type=EntityType.FINDING,
        entity_id=str(vulnerabilidade.id),
        old_value={"status": anterior.value} if anterior else None,
        new_value={"status": dados.status.value},
        metadata_info=metadata if metadata else None
    )

    db.commit()
    db.refresh(vulnerabilidade)

    return detalhar(vulnerabilidade_id, db)


@router.post("/{vulnerabilidade_id}/analise", response_model=VulnerabilidadeDetalhe)
def gerar_analise_ia(
    vulnerabilidade_id: int, db: Session = Depends(get_db)
) -> VulnerabilidadeDetalhe:
    """
    Gera a explicação da IA para esta vulnerabilidade.

    Sob demanda, e não durante o upload, por dois motivos: um relatório grande
    faria dezenas de chamadas e deixaria o envio lento, e nem toda
    vulnerabilidade precisa de explicação — o usuário pede quando vai tratar.

    A IA recebe o risco já decidido e apenas o explica. Os dados sensíveis são
    mascarados antes do envio.
    """
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    aplicacao = db.get(Application, vulnerabilidade.aplicacao_id)
    assert aplicacao is not None

    try:
        gerar_analise(db, vulnerabilidade, aplicacao)
    except IANaoConfiguradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except ErroProvedorIA as exc:
        # A falha da IA não invalida a vulnerabilidade: risco, justificativa e
        # acompanhamento seguem válidos. Só a explicação ficou indisponível.
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return detalhar(vulnerabilidade_id, db)


@router.patch("/{vulnerabilidade_id}/owner", response_model=VulnerabilidadeDetalhe)
def atribuir_owner(
    vulnerabilidade_id: int,
    dados: AtribuicaoRequest,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service),
) -> VulnerabilidadeDetalhe:
    """
    Atribui um responsÃ¡vel pela remediaÃ§Ã£o da vulnerabilidade.
    """
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)
    anterior_id = vulnerabilidade.owner_id

    vulnerabilidade.owner_id = dados.owner_id
    vulnerabilidade.owner_team = dados.owner_team
    if dados.owner_id and not vulnerabilidade.assigned_at:
        vulnerabilidade.assigned_at = datetime.now(UTC)

    db.commit()

    audit.log_action(
        action=AuditAction.ASSIGNMENT_CHANGED,
        actor_user_id=usuario.id,
        entity_type=EntityType.FINDING,
        entity_id=str(vulnerabilidade.id),
        old_value={"owner_id": anterior_id},
        new_value={"owner_id": dados.owner_id, "owner_team": dados.owner_team},
    )

    return detalhar(vulnerabilidade_id, db)


@router.post("/{vulnerabilidade_id}/comments", response_model=CommentResponse)
def adicionar_comentario(
    vulnerabilidade_id: int,
    dados: CommentCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
    audit: AuditService = Depends(get_audit_service),
) -> CommentResponse:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)

    comentario = RemediationComment(
        vulnerability_id=vulnerabilidade.id,
        author_id=usuario.id,
        content=dados.content
    )
    db.add(comentario)
    db.commit()
    db.refresh(comentario)

    audit.log_action(
        action=AuditAction.COMMENT_ADDED,
        actor_user_id=usuario.id,
        entity_type=EntityType.COMMENT,
        entity_id=str(comentario.id),
        metadata_info={"vulnerability_id": vulnerabilidade.id}
    )

    resposta = CommentResponse.model_validate(comentario)
    resposta.author_name = usuario.nome
    return resposta


@router.get("/{vulnerabilidade_id}/comments", response_model=list[CommentResponse])
def listar_comentarios(
    vulnerabilidade_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> list[CommentResponse]:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)

    resultados = []
    for c in vulnerabilidade.comments:
        item = CommentResponse.model_validate(c)
        item.author_name = c.author.nome if c.author else None
        resultados.append(item)

    return resultados


@router.post("/{vulnerabilidade_id}/evidences", response_model=EvidenceResponse)
def adicionar_evidencia(
    vulnerabilidade_id: int,
    dados: EvidenceCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:write")),
    audit: AuditService = Depends(get_audit_service),
) -> EvidenceResponse:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)

    evidencia = RemediationEvidence(
        vulnerability_id=vulnerabilidade.id,
        author_id=usuario.id,
        evidence_type=dados.evidence_type,
        description=dados.description,
        reference=dados.reference
    )
    db.add(evidencia)
    db.commit()
    db.refresh(evidencia)

    audit.log_action(
        action=AuditAction.EVIDENCE_ADDED,
        actor_user_id=usuario.id,
        entity_type=EntityType.EVIDENCE,
        entity_id=str(evidencia.id),
        metadata_info={"vulnerability_id": vulnerabilidade.id, "type": dados.evidence_type}
    )

    resposta = EvidenceResponse.model_validate(evidencia)
    resposta.author_name = usuario.nome
    return resposta


@router.get("/{vulnerabilidade_id}/evidences", response_model=list[EvidenceResponse])
def listar_evidencias(
    vulnerabilidade_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(RequirePermission("finding:read")),
) -> list[EvidenceResponse]:
    vulnerabilidade = _buscar_ou_404(db, vulnerabilidade_id)

    resultados = []
    for e in vulnerabilidade.evidences:
        item = EvidenceResponse.model_validate(e)
        item.author_name = e.author.nome if e.author else None
        resultados.append(item)

    return resultados


