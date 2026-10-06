# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.models.integration import Integration


def test_jira_authorize_redirects(client: TestClient, auth: dict[str, str]):
    """AC-JIRA-01: ..."""
    resp = client.get("/api/integrations/jira/authorize", headers=auth)
    assert resp.status_code == 200
    dados = resp.json()
    url = dados["url"]


    assert "auth.atlassian.com/authorize" in url
    assert "state=" in url
    assert "scope=" in url
    assert "offline_access" in url


@patch("app.routers.integrations.httpx.post")
@patch("app.routers.integrations.httpx.get")
def test_jira_callback_success(mock_get, mock_post, client: TestClient, db: Session, auth: dict[str, str]):
    """AC-JIRA-02: ..."""
    # Setup signed state token
    payload = {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)}
    state = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


    mock_post_resp = MagicMock()
    mock_post_resp.status_code = 200
    mock_post_resp.json.return_value = {
        "access_token": "fake_access",
        "refresh_token": "fake_refresh",
        "expires_in": 3600
    }
    mock_post.return_value = mock_post_resp


    mock_get_resp = MagicMock()
    mock_get_resp.status_code = 200
    mock_get_resp.json.return_value = [
        {"id": "cloud-id-123", "url": "https://test.atlassian.net"}
    ]
    mock_get.return_value = mock_get_resp


    # Executa o callback
    resp = client.get(f"/api/integrations/jira/callback?code=abc123&state={state}", follow_redirects=False)


    assert resp.status_code == 307  # RedirectResponse returns 307
    assert "integracoes?jira=success" in resp.headers["location"]


    # Verifica DB
    integ = db.query(Integration).filter_by(user_id=1, provider="jira").first()
    assert integ is not None
    assert integ.cloud_id == "cloud-id-123"
    assert integ.access_token_enc is not None
    assert integ.refresh_token_enc is not None


def test_jira_callback_invalid_state(client: TestClient):
    resp = client.get("/api/integrations/jira/callback?code=abc123&state=forged_token")
    """AC-JIRA-03: ..."""
    resp = client.get("/api/integrations/jira/callback?code=abc123&state=forged_token")
    assert resp.status_code == 400
    assert "State inválido" in resp.json()["detail"]

