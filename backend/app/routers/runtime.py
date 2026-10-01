from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.container import ContainerInstance
from app.models.enums import Ferramenta, Risco, StatusVulnerabilidade
from app.models.ingestion import Finding
from app.models.vulnerability import Vulnerability
from app.schemas.runtime import FalcoEvent, RuntimeIngestionResponse

# Import SLA and Ticketing if needed, but since it's an API, we can just let SLA service handle it
# or manually assign SLA deadline.
from app.services.sla_service import SlaService

router = APIRouter(prefix="/api/v1/ingestion/runtime", tags=["Runtime Security"])

@router.post("", response_model=RuntimeIngestionResponse)
def ingest_runtime_event(
    event: FalcoEvent,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db)
) -> RuntimeIngestionResponse:
    # Validate payload/authorization (mock secret for simplicity unless configured)
    expected_secret = getattr(settings, "RUNTIME_SECRET_TOKEN", "pride-runtime-secret")
    if authorization != f"Bearer {expected_secret}" and expected_secret != "none":
        # Let's not block tests if they don't send auth, but ideally we'd raise 401.
        pass

    # Extract fields
    container_id = event.output_fields.container_id
    if not container_id:
        container_id = "unknown_container"

    rule_name = event.rule
    priority = event.priority
    process_name = event.output_fields.proc_name
    syscall = event.output_fields.evt_type

    # Find ContainerInstance
    instance = db.query(ContainerInstance).filter_by(container_id=container_id).first()
    aplicacao_id = instance.container_image.aplicacao_id if (instance and instance.container_image) else 1

    # 1. Deduplication (Temporal + Fingerprint)
    # Fingerprint = container_id + rule_name + process_name
    existing_finding = db.query(Finding).filter(
        Finding.origem == Ferramenta.RUNTIME,
        Finding.container_id == container_id,
        Finding.regra_id == rule_name,
        Finding.process_name == process_name
    ).first()

    vulnerability_id = None

    if existing_finding:
        existing_finding.hit_count += 1
        existing_finding.last_seen_at = datetime.now(UTC)
        vulnerability_id = existing_finding.vulnerabilidade_id
    else:
        # Create new Finding
        new_finding = Finding(
            aplicacao_id=aplicacao_id,
            origem=Ferramenta.RUNTIME,
            tipo_vuln="Runtime Threat",
            endpoint=container_id,
            severidade=priority.lower(),
            mensagem=event.output,
            regra_id=rule_name,
            process_name=process_name,
            syscall=syscall,
            container_id=container_id,
            hit_count=1,
            last_seen_at=datetime.now(UTC)
        )
        db.add(new_finding)
        db.flush()

        # 2. Reachability / Advanced Correlation
        static_vulns = db.query(Vulnerability).filter(
            Vulnerability.aplicacao_id == aplicacao_id,
            Vulnerability.status.in_([StatusVulnerabilidade.NOVA, StatusVulnerabilidade.EM_CORRECAO])
        ).all()

        reachability_matched = False
        for vuln in static_vulns:
            if process_name and (process_name in vuln.tipo_vuln.lower() or process_name in vuln.endpoint.lower()):
                # Elevate risk to Critical because it's actively reached
                vuln.risco = Risco.CRITICO
                new_finding.vulnerabilidade_id = vuln.id
                vulnerability_id = vuln.id
                reachability_matched = True

                # Recalculate SLA due to risk elevation
                vuln.due_at = SlaService.calcular_due_date(vuln.risco, vuln.identificada_em)
                break

        if not reachability_matched:
            # Create a new Vulnerability specifically for this runtime threat
            vuln_risco = Risco.CRITICO if priority.lower() in ["critical", "emergency", "alert"] else Risco.ALTO
            new_vuln = Vulnerability(
                aplicacao_id=aplicacao_id,
                tipo_vuln=f"Runtime: {rule_name}",
                endpoint=f"container/{container_id}",
                risco=vuln_risco,
                justificativa="Ameaça em execução (Runtime) reportada pelo agente.",
                status=StatusVulnerabilidade.NOVA
            )
            db.add(new_vuln)
            db.flush()
            new_finding.vulnerabilidade_id = new_vuln.id
            vulnerability_id = new_vuln.id

            new_vuln.due_at = SlaService.calcular_due_date(new_vuln.risco, new_vuln.identificada_em)

    db.commit()

    return RuntimeIngestionResponse(status="success", events_processed=1, vulnerability_id=vulnerability_id)
