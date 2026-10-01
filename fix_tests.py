import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.enums import Role
from app.models.user import User

def test_ac_obs_01_request_id_in_headers(client: TestClient, auth: dict[str, str]):
    """AC-OBS-01 — correlation_id"""
    response = client.get("/api/saude", headers={"X-Request-ID": "test-id-123"})
    assert response.status_code == 200

def test_ac_obs_03_metrics_protected_admin_only(
    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]
):
    """AC-OBS-03 — metrics admin"""
    resp_unauth = client.get("/metrics")
    assert resp_unauth.status_code == 401

    user = db.query(User).filter(User.email == usuario_cadastrado["email"]).first()
    
    # Testa DEVELOPER
    user.role = Role.DEVELOPER
    db.commit()
    resp_dev = client.get("/metrics", headers=auth)
    assert resp_dev.status_code == 403

    # Testa ADMIN
    user.role = Role.ADMIN
    db.commit()
    resp_admin = client.get("/metrics", headers=auth)
    assert resp_admin.status_code == 200
    assert "http_requests_total" in resp_admin.text

def test_ac_obs_04_deep_health_check(client: TestClient):
    """AC-OBS-04 — deep health"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["database"] == "up"

def test_ac_obs_02_middleware_increments_metric(
    client: TestClient, db: Session, auth: dict[str, str], usuario_cadastrado: dict[str, str]
):
    """AC-OBS-02 — middleware increments"""
    client.get("/api/saude")
    
    user = db.query(User).filter(User.email == usuario_cadastrado["email"]).first()
    user.role = Role.ADMIN
    db.commit()

    resp_admin = client.get("/metrics", headers=auth)
    assert 'route="/api/saude"' in resp_admin.text
