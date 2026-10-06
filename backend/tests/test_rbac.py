# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import Role
from app.models.user import User


def test_rbac_developer_cannot_create_app(
    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]
):
    # Demote to DEVELOPER
    user = db.query(User).filter(User.email == usuario_cadastrado["email"]).first()
    user.role = Role.DEVELOPER
    db.commit()

    # Developer cannot create app
    resp = client.post(
        "/api/aplicacoes",
        headers=auth,
        json={
            "nome": "App Teste",
            "responsavel": "Dev",
            "ambiente": "teste",
            "exposicao": "interna",
            "importancia": "baixa",
        },
    )
    assert resp.status_code == 403
    assert "permissão insuficiente" in resp.json()["detail"]


def test_rbac_admin_can_create_app(
    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]
):
    user = db.query(User).filter(User.email == usuario_cadastrado["email"]).first()
    user.role = Role.ADMIN
    db.commit()

    resp = client.post(
        "/api/aplicacoes",
        headers=auth,
        json={
            "nome": "App Teste 2",
            "responsavel": "Admin",
            "ambiente": "teste",
            "exposicao": "interna",
            "importancia": "baixa",
        },
    )
    assert resp.status_code == 201


def test_rbac_auditor_cannot_close_finding(
    client: TestClient,
    db: Session,
    auth: dict[str, str],
    aplicacao_producao: dict[str, object],
    usuario_cadastrado: dict[str, str],
):
    # Create vulnerability
    resp = client.post(
        f"/api/aplicacoes/{aplicacao_producao['id']}/uploads/semgrep",
        headers=auth,
        files={
            "arquivo": ("relatorio.json", b'{"results": []}')
        },  # We need some valid JSON, but let's mock the parsing or just use a minimal valid one if possible. Wait, to just change status we can mock a finding directly in DB.
    )

    # Just insert a finding directly to test closing
    from datetime import UTC, datetime

    from app.models import Risco, StatusVulnerabilidade, Vulnerability

    vuln = Vulnerability(
        aplicacao_id=aplicacao_producao["id"],
        tipo_vuln="teste",
        endpoint="/",
        risco=Risco.BAIXO,
        status=StatusVulnerabilidade.NOVA,
        identificada_em=datetime.now(UTC),
        atualizada_em=datetime.now(UTC),
        justificativa="",
    )
    db.add(vuln)
    db.commit()

    # Demote to AUDITOR
    user = db.query(User).filter(User.email == usuario_cadastrado["email"]).first()
    user.role = Role.AUDITOR
    db.commit()

    resp = client.patch(
        f"/api/vulnerabilidades/{vuln.id}/status",
        headers=auth,
        json={"status": "corrigida", "comentario": "teste"},
    )
    assert resp.status_code == 403
