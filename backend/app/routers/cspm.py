# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.cloud import CloudAccount, CloudResource
from app.models.enums import Ferramenta, Risco
from app.models.ingestion import Finding
from app.models.vulnerability import Vulnerability
from app.schemas.cspm import CSPMEvent
from app.services.sla_service import SlaService

router = APIRouter(prefix="/api/v1/ingestion", tags=["Ingestion"])

def severity_to_risco(sev: str) -> Risco:
    s = sev.upper()
    if s == "CRITICAL":
        return Risco.CRITICO
    if s == "HIGH":
        return Risco.ALTO
    if s == "MEDIUM":
        return Risco.MEDIO
    return Risco.BAIXO

@router.post("/cspm")
def ingest_cspm_event(
    event: CSPMEvent,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    # Validacao basica de webhook secret
    if authorization != "Bearer pride-cspm-secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # 1. Garantir CloudAccount e CloudResource
    account = db.query(CloudAccount).filter_by(account_id=event.account_id, provider=event.provider).first()
    if not account:
        account = CloudAccount(account_id=event.account_id, provider=event.provider)
        db.add(account)
        db.commit()
        db.refresh(account)

    resource = db.query(CloudResource).filter_by(arn_or_uri=event.resource_id).first()
    if not resource:
        resource = CloudResource(
            cloud_account_id=account.id,
            arn_or_uri=event.resource_id,
            resource_type=event.resource_type,
            region=event.region
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)

    # 2. Descobrir aplicacao (CMDB lookup ficticio ou relacionamento real)
    # Aqui, assumimos que o recurso esta atrelado a uma Application pelo ARN ou que o CMDB ja preencheu
    # Se nao achar, associamos a aplicacao 1 por padrao de fallback em testes
    app_id = resource.aplicacao_id
    if not app_id:
        app_db = db.query(Application).first()
        app_id = app_db.id if app_db else 1 # para nao quebrar a constraint de vulnerabilidade. Em prod, seria tratado melhor.

    # 3. Deduplicacao temporal do Achado
    finding = db.query(Finding).filter(
        Finding.origem == Ferramenta.CLOUD_POSTURE,
        Finding.endpoint == event.resource_id,
        Finding.tipo_vuln == event.title,
        Finding.aplicacao_id == app_id
    ).first()

    if finding:
        finding.hit_count += 1
        finding.last_seen_at = datetime.now(UTC)
        db.commit()
        vuln = db.query(Vulnerability).filter_by(id=finding.vulnerabilidade_id).first()
        return {"status": "updated", "hit_count": finding.hit_count, "vulnerability_id": vuln.id if vuln else None}

    # 4. Inserir Achado novo e criar Vulnerabilidade
    risco_inicial = severity_to_risco(event.severity)

    # Risk Engine basico p/ nuvem: Exposto = risco maximo
    if "0.0.0.0/0" in event.description or "public" in event.title.lower():
        risco_inicial = Risco.CRITICO

    vuln = Vulnerability(
        aplicacao_id=app_id,
        tipo_vuln=event.title,
        endpoint=event.resource_id,
        risco=risco_inicial,
        justificativa="Misconfiguration detectada por CSPM",
        severidade_original=event.severity.lower()
    )
    vuln.identificada_em = datetime.now(UTC)
    vuln.due_at = SlaService.calcular_due_date(vuln.risco, vuln.identificada_em)

    db.add(vuln)
    db.commit()
    db.refresh(vuln)

    new_finding = Finding(
        aplicacao_id=app_id,
        vulnerabilidade_id=vuln.id,
        origem=Ferramenta.CLOUD_POSTURE,
        tipo_vuln=event.title,
        endpoint=event.resource_id,
        severidade=event.severity.lower(),
        mensagem=event.description,
        regra_id=event.compliance_control or event.title,
        cloud_provider=event.provider,
        region=event.region,
        compliance_control=event.compliance_control,
        hit_count=1,
        last_seen_at=datetime.now(UTC)
    )
    db.add(new_finding)
    db.commit()

    # 5. Correlação de Toxic Combinations (Drift ou RCE Exposto)
    # Verifica se existe uma vuln ativa nesta aplicacao (mesmo resource_id ou container associado)
    # que faca uma Toxic Combination.
    # Exemplo: O container atrelado ao resource tem RCE
    # Aqui procuraremos de forma otimista
    vulns_ativas = db.query(Vulnerability).filter(
        Vulnerability.aplicacao_id == app_id,
        Vulnerability.status.in_(["nova", "triada", "em_correcao"]),
        Vulnerability.id != vuln.id
    ).all()

    toxic_combo = False
    for v in vulns_ativas:
        # Se for RCE ou "Remote Code Execution" e este recurso estiver publico, Toxic Combination!
        if ("RCE" in v.tipo_vuln.upper() or "REMOTE" in v.tipo_vuln.upper()) and risco_inicial == Risco.CRITICO:
            v.risco = Risco.CRITICO
            v.justificativa = "Toxic Combination: RCE em ambiente publicamente exposto pelo CSPM!"
            v.due_at = SlaService.calcular_due_date(v.risco, v.identificada_em)
            toxic_combo = True
            break

    db.commit()

    return {
        "status": "created",
        "finding_id": new_finding.id,
        "vulnerability_id": vuln.id,
        "toxic_combination_detected": toxic_combo
    }
