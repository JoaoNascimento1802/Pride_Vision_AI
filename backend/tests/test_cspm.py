# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.cloud import CloudAccount, CloudResource
from app.models.enums import Risco, StatusVulnerabilidade
from app.models.vulnerability import Vulnerability


def test_ac_cspm_01_ingest_and_deduplicate(db: Session, client: TestClient):
    """AC-CSPM-01 - Webhook."""
    # Criar aplicacao mock
    app_name = f"App_{uuid.uuid4().hex}"
    app = Application(
        nome=app_name,
        responsavel="Admin",
        ambiente="producao",
        exposicao="interna",
        importancia="alta"
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Assumimos fallback app id = 1 pra simplificar ou criar resource atrelado
    # Pra este teste vamos forçar app.id == 1 via seed se for a primeira vez

    payload = {
        "provider": "aws",
        "account_id": "123456789012",
        "resource_id": f"arn:aws:s3:::{uuid.uuid4().hex}",
        "resource_type": "s3_bucket",
        "region": "us-east-1",
        "compliance_framework": "CIS",
        "compliance_control": "1.4",
        "severity": "HIGH",
        "title": "S3 Bucket sem encryption",
        "description": "Bucket exposed"
    }

    # Ingest
    headers = {"authorization": "Bearer pride-cspm-secret"}
    resp = client.post("/api/v1/ingestion/cspm", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "created"

    # Check deduplication
    resp2 = client.post("/api/v1/ingestion/cspm", json=payload, headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "updated"
    assert data2["hit_count"] == 2

def test_ac_cspm_02_toxic_combination(db: Session, client: TestClient):
    """AC-CSPM-02 - Toxic Combination."""
    # Criar aplicacao
    app = Application(
        nome=f"App_{uuid.uuid4().hex}",
        responsavel="Admin",
        ambiente="producao",
        exposicao="interna",
        importancia="alta"
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    app_id = app.id

    # Criar vulnerability de RCE
    vuln = Vulnerability(
        aplicacao_id=app_id,
        tipo_vuln="Remote Code Execution via Log4j",
        endpoint="/api/login",
        risco=Risco.ALTO,
        justificativa="Detectado no container",
        status=StatusVulnerabilidade.NOVA
    )
    db.add(vuln)
    db.commit()
    db.refresh(vuln)

    # Modificar router para aceitar app_id pra forcar o teste a ser isolado,
    # Ou injetar o resource antes de ingestar
    resource_id = f"arn:aws:ec2:us-east-1:123456789012:instance/i-{uuid.uuid4().hex}"
    acc = CloudAccount(account_id="123456789012", provider="aws")
    db.add(acc)
    db.commit()
    db.refresh(acc)

    res = CloudResource(cloud_account_id=acc.id, arn_or_uri=resource_id, resource_type="ec2", region="us-east-1", aplicacao_id=app_id)
    db.add(res)
    db.commit()

    payload = {
        "provider": "aws",
        "account_id": "123456789012",
        "resource_id": resource_id,
        "resource_type": "ec2",
        "region": "us-east-1",
        "severity": "CRITICAL",
        "title": "Security Group exposto publicamente",
        "description": "Porta 22 aberta para 0.0.0.0/0"
    }

    headers = {"authorization": "Bearer pride-cspm-secret"}
    resp = client.post("/api/v1/ingestion/cspm", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["toxic_combination_detected"] is True

    db.refresh(vuln)
    assert vuln.risco == Risco.CRITICO
    assert "Toxic Combination" in vuln.justificativa
