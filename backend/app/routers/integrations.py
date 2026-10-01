"""
integrations.py — Endpoints para Webhooks e integrações externas.

POST /api/integrations/webhooks/github
POST /api/integrations/webhooks/gitlab
GET  /api/integrations/status
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import usuario_atual
from app.config import settings
from app.database import get_db
from app.models.enums import AuditAction, EntityType
from app.models.integration import Integration
from app.services.audit import AuditService, get_audit_service
from app.services.crypto import encrypt_token

router = APIRouter(
    prefix="/api/integrations",
    tags=["Integrations & Webhooks"],
)


def _verificar_assinatura_github(payload: bytes, signature_header: str | None) -> bool:
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        return False
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected_mac = hmac.new(
        secret.encode("utf-8"), msg=payload, digestmod=hashlib.sha256
    ).hexdigest()

    received_mac = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected_mac, received_mac)


def _verificar_assinatura_gitlab(token_header: str | None) -> bool:
    secret = settings.GITLAB_WEBHOOK_SECRET
    if not secret:
        return False
    if not token_header:
        return False

    return hmac.compare_digest(secret, token_header)


@router.post("/webhooks/github", status_code=status.HTTP_200_OK)
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
    x_github_delivery: str | None = Header(None),
) -> Any:
    """
    Recebe eventos do GitHub (ex: pull_request, push).
    Valida a assinatura (HMAC-SHA256) com tempo constante.
    """
    payload = await request.body()

    if not _verificar_assinatura_github(payload, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Assinatura inválida ou ausente.",
        )

    # Previne processamento duplicado se o evento já foi processado
    # Aqui armazenaríamos o delivery_id em uma tabela AuditLog ou WebhookLog.
    # Como não temos ainda tabela de webhook log, apenas aceitamos.
    if not x_github_event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento desconhecido")

    # A integração completa avaliaria o payload.json()
    # ex: acionar o pipeline_check de forma assíncrona se for um PR aberto.

    return {"status": "accepted", "delivery_id": x_github_delivery, "event": x_github_event}


@router.post("/webhooks/gitlab", status_code=status.HTTP_200_OK)
async def gitlab_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_gitlab_token: str | None = Header(None),
    x_gitlab_event: str | None = Header(None),
) -> Any:
    """
    Recebe eventos do GitLab.
    Valida o X-Gitlab-Token com tempo constante.
    """
    if not _verificar_assinatura_gitlab(x_gitlab_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou ausente.",
        )

    if not x_gitlab_event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evento desconhecido")

    return {"status": "accepted", "event": x_gitlab_event}




@router.get("/jira/authorize")
def jira_authorize(
    request: Request, user: Any = Depends(usuario_atual)
) -> Any:
    """
    Inicia o fluxo OAuth 2.0 (3LO) para o Jira.
    """
    # State token: protege contra CSRF, válido por 10 minutos
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(UTC) + timedelta(minutes=10)
    }
    state = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


    url = (
        "https://auth.atlassian.com/authorize?"
        "audience=api.atlassian.com&"
        f"client_id={settings.JIRA_CLIENT_ID}&"
        f"scope={settings.JIRA_SCOPES.replace(' ', '%20')}&"
        f"redirect_uri={settings.JIRA_REDIRECT_URI}&"
        f"state={state}&"
        "response_type=code&"
        "prompt=consent"
    )
    return {"url": url}

@router.get("/jira/callback")
def jira_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    audit: AuditService = Depends(get_audit_service)
) -> Any:
    """
    Callback do OAuth 2.0 Atlassian.
    """
    try:
        payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State inválido ou expirado"
        )


    token_url = "https://auth.atlassian.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.JIRA_CLIENT_ID,
        "client_secret": settings.JIRA_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.JIRA_REDIRECT_URI,
    }
    resp = httpx.post(token_url, json=data)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao trocar código por token: {resp.text}"
        )


    token_data = resp.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)


    # Descobre o site autorizado
    headers = {"Authorization": f"Bearer {access_token}"}
    res_resp = httpx.get("https://api.atlassian.com/oauth/token/accessible-resources", headers=headers)
    if res_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha ao listar resources")


    resources = res_resp.json()
    if not resources:
        raise HTTPException(status_code=400, detail="Nenhum site Jira autorizado")


    cloud_id = resources[0]["id"]
    site_url = resources[0]["url"]


    integ = db.query(Integration).filter_by(user_id=user_id, provider="jira").first()
    if not integ:
        integ = Integration(user_id=user_id, provider="jira")
        db.add(integ)


    integ.cloud_id = cloud_id
    integ.site_url = site_url
    integ.access_token_enc = encrypt_token(access_token)
    if refresh_token:
        integ.refresh_token_enc = encrypt_token(refresh_token)
    integ.expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)


    audit.log_action(
        action=AuditAction.JIRA_CONNECT,
        actor_user_id=user_id,
        entity_type=EntityType.INTEGRATION,
        entity_id=str(integ.id),
        new_value={"site_url": site_url, "cloud_id": cloud_id}
    )

    db.commit()


    return RedirectResponse(url=f"{settings.FRONTEND_URL}/integracoes?jira=success")

@router.get("/status", dependencies=[Depends(usuario_atual)])
def status_integracoes(
    user: Any = Depends(usuario_atual),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retorna o status das integrações (GitHub / GitLab / Jira) para o frontend.
    """
    github_status = (
        "Connected" if settings.GITHUB_APP_ID and settings.GITHUB_PRIVATE_KEY else "Not configured"
    )
    gitlab_status = "Available" if settings.GITLAB_TOKEN else "Not configured"


    jira_integ = db.query(Integration).filter_by(user_id=user.id, provider="jira").first()
    jira_status = "Connected" if jira_integ and jira_integ.access_token_enc else "Not configured"

    return {
        "github": github_status,
        "gitlab": gitlab_status,
        "jira": jira_status,
        "jira_site": jira_integ.site_url if jira_integ else None
    }
