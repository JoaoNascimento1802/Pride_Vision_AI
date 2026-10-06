# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import Ambiente, Exposicao, Importancia, Risco, TicketProvider, TicketStatus
from app.models.integration import Integration
from app.models.ticket import Ticket
from app.models.vulnerability import Vulnerability
from app.services.crypto import encrypt_token


@pytest.fixture
def mock_httpx_request():
    with (
        patch("app.services.ticketing.httpx.request") as mock_req,
        patch("app.services.ticketing.httpx.post") as mock_post,
    ):
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {"access_token": "new_fake", "expires_in": 3600}
        mock_post.return_value = mock_post_resp
        yield mock_req


def test_criar_ticket(client: TestClient, db: Session, auth: dict[str, str], mock_httpx_request):
    """AC-JIRA-04, AC-JIRA-05, AC-JIRA-06"""
    from app.models.user import User

    user = db.query(User).filter_by(email="ana@exemplo.com").first()
    # Setup Integration
    integ = Integration(
        user_id=user.id,
        provider="jira",
        cloud_id="fake-cloud-id",
        site_url="https://fake.atlassian.net",
        access_token_enc=encrypt_token("fake_access"),
        refresh_token_enc=encrypt_token("fake_refresh"),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    db.add(integ)
    db.commit()

    app = Application(
        nome="App Tickets",
        responsavel="Time",
        ambiente=Ambiente.PRODUCAO,
        exposicao=Exposicao.INTERNA,
        importancia=Importancia.BAIXA,
    )
    db.add(app)
    db.commit()

    vuln = Vulnerability(
        aplicacao_id=app.id,
        tipo_vuln="SQL Injection",
        endpoint="/api/users",
        risco=Risco.ALTO,
        justificativa="Teste",
    )
    db.add(vuln)
    db.commit()
    db.refresh(vuln)

    # Configurar mock
    mock_resp_proj = MagicMock()
    mock_resp_proj.status_code = 200
    mock_resp_proj.json.return_value = [{"id": "10000"}]

    mock_resp_meta = MagicMock()
    mock_resp_meta.status_code = 200
    mock_resp_meta.json.return_value = {
        "projects": [{"issuetypes": [{"id": "10001", "name": "Bug"}]}]
    }

    mock_resp_issue = MagicMock()
    mock_resp_issue.status_code = 201
    mock_resp_issue.json.return_value = {"id": "100", "key": "PRJ-100"}

    mock_httpx_request.side_effect = [mock_resp_proj, mock_resp_meta, mock_resp_issue]

    resp = client.post(
        f"/api/vulnerabilidades/{vuln.id}/tickets", headers=auth, json={"provider": "jira"}
    )
    assert resp.status_code == 201, resp.json()
    dados = resp.json()
    assert dados["provider"] == "jira"
    assert dados["status"] == "open"
    assert dados["external_key"] == "PRJ-100"
    assert dados["external_id"] == "100"
    assert mock_httpx_request.call_count == 3


def test_sincronizar_ticket(
    client: TestClient, db: Session, auth: dict[str, str], mock_httpx_request
):
    """AC-JIRA-07, AC-JIRA-08, AC-JIRA-09"""
    from app.models.user import User

    user = db.query(User).filter_by(email="ana@exemplo.com").first()

    integ = Integration(
        user_id=user.id,
        provider="jira",
        cloud_id="fake-cloud-id",
        site_url="https://fake.atlassian.net",
        access_token_enc=encrypt_token("fake_access"),
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    db.add(integ)
    db.commit()

    app = Application(
        nome="App Tickets 2",
        responsavel="Time",
        ambiente=Ambiente.PRODUCAO,
        exposicao=Exposicao.INTERNA,
        importancia=Importancia.BAIXA,
    )
    db.add(app)
    db.commit()

    vuln = Vulnerability(
        aplicacao_id=app.id,
        tipo_vuln="XSS",
        endpoint="/api/comments",
        risco=Risco.MEDIO,
        justificativa="Teste",
    )
    db.add(vuln)
    db.commit()

    ticket = Ticket(
        vulnerabilidade_id=vuln.id,
        provider=TicketProvider.JIRA,
        external_id="123",
        external_key="PRJ-123",
        url="https://fake.atlassian.net/browse/PRJ-123",
        title="[MEDIO] XSS",
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.commit()

    mock_resp_sync = MagicMock()
    mock_resp_sync.status_code = 200
    mock_resp_sync.json.return_value = {
        "fields": {"summary": "Updated Title", "status": {"statusCategory": {"key": "done"}}}
    }
    mock_httpx_request.side_effect = [mock_resp_sync]

    resp = client.post(f"/api/vulnerabilidades/{vuln.id}/tickets/{ticket.id}/sync", headers=auth)

    assert resp.status_code == 200, resp.json()
    dados = resp.json()
    assert dados["status"] == "resolved"
    assert dados["title"] == "Updated Title"
