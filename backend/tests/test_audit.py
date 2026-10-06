# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.


from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.enums import AuditAction, EntityType
from app.services.audit import AuditService, sanitize_data
from tests.conftest import SENHA_PADRAO


def test_sanitize_data() -> None:
    """AC-AUDIT-01: Mascaramento de dados sensíveis."""
    payload = {
        "normal": "value",
        "nested": {
            "password": "secret_password",
            "access_token": "token123",
            "api_key": "key456"
        },
        "list": [
            {"client_secret": "my_secret"}
        ]
    }

    sanitized = sanitize_data(payload)
    assert sanitized["normal"] == "value"
    assert sanitized["nested"]["password"] == "[REDACTED]"
    assert sanitized["nested"]["access_token"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["list"][0]["client_secret"] == "[REDACTED]"


def test_audit_service_log_action(db: Session) -> None:
    """Testa se o serviço salva corretamente no banco."""
    service = AuditService(db=db)
    log = service.log_action(
        action=AuditAction.LOGIN_SUCCESS,
        actor_user_id=None,
        entity_type=EntityType.USER,
        entity_id="123",
        old_value={"status": "old"},
        new_value={"status": "new", "password": "123"},
        metadata_info={"ip": "127.0.0.1"}
    )

    db.commit()

    saved = db.query(AuditLog).filter_by(id=log.id).first()
    assert saved is not None
    assert saved.action == AuditAction.LOGIN_SUCCESS
    assert saved.entity_id == "123"
    assert saved.new_value["password"] == "[REDACTED]"


def test_get_audit_logs_unauthorized(client: TestClient) -> None:
    """AC-AUDIT-07: Usuário sem permissão."""
    resp = client.get("/api/audit")
    assert resp.status_code == 401


def test_get_audit_logs_authorized(client: TestClient, auth: dict[str, str]) -> None:
    """AC-AUDIT-06: Paginação e acesso."""
    resp = client.get("/api/audit?skip=0&limit=10", headers=auth)
    assert resp.status_code == 200
    assert "items" in resp.json()
    assert "total" in resp.json()


def test_audit_log_immutability(client: TestClient, auth: dict[str, str]) -> None:
    """AC-AUDIT-02: Imutabilidade."""
    resp_delete = client.delete("/api/audit/1", headers=auth)
    assert resp_delete.status_code == 404

    resp_put = client.put("/api/audit/1", json={"action": "HACK"}, headers=auth)
    assert resp_put.status_code == 404


def test_audit_login_success_action(client: TestClient, db: Session, usuario_cadastrado: dict[str, str]) -> None:
    """AC-AUDIT-03: Registro de login success"""
    resp = client.post(
        "/api/auth/login",
        data={"username": usuario_cadastrado["email"], "password": SENHA_PADRAO},
    )
    assert resp.status_code == 200

    logs = db.query(AuditLog).filter_by(action=AuditAction.LOGIN_SUCCESS).all()
    assert len(logs) > 0


def test_audit_login_failure_action(client: TestClient, db: Session, usuario_cadastrado: dict[str, str]) -> None:
    """AC-AUDIT-03: Registro de login failure"""
    resp = client.post(
        "/api/auth/login",
        data={"username": usuario_cadastrado["email"], "password": "senha_errada"},
    )
    assert resp.status_code == 401

    logs = db.query(AuditLog).filter_by(action=AuditAction.LOGIN_FAILURE).all()
    assert len(logs) > 0


def test_audit_action_status_changed(client: TestClient, db: Session, auth: dict[str, str], aplicacao_producao: dict[str, object]) -> None:
    """AC-AUDIT-04: Vulnerability Status Changed"""
    from app.models.enums import Risco, StatusVulnerabilidade
    from app.models.vulnerability import Vulnerability

    v = Vulnerability(
        aplicacao_id=aplicacao_producao['id'],
        tipo_vuln="XSS",
        endpoint="/busca",
        risco=Risco.ALTO,
        status=StatusVulnerabilidade.NOVA,
        justificativa="Test"
    )
    db.add(v)
    db.commit()
    db.refresh(v)

    resp = client.patch(
        f"/api/vulnerabilidades/{v.id}/status",
        json={"status": "em_analise", "comentario": "Analise"},
        headers=auth
    )
    assert resp.status_code == 200

    logs = db.query(AuditLog).filter_by(action=AuditAction.STATUS_CHANGED).all()
    assert len(logs) > 0


def test_audit_action_gate_executed(client: TestClient, db: Session, auth: dict[str, str], aplicacao_producao: dict[str, object]) -> None:
    """AC-AUDIT-05: Gate Executed"""
    resp = client.post(
        "/api/ci/check",
        json={
            "application_id": aplicacao_producao['id'],
            "commit_sha": "abc1234",
            "branch": "main",
            "environment": "production",
            "pipeline_id": "pip1",
            "run_id": "run1",
            "provider": "github"
        },
        headers=auth
    )
    assert resp.status_code == 200

    logs = db.query(AuditLog).filter_by(action=AuditAction.GATE_EXECUTED).all()
    assert len(logs) > 0
