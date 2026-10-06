# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.


"""
auth.py — Rotas de cadastro, login e identificação do usuário.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import usuario_atual
from app.auth.security import SenhaMuitoLongaError, criar_token, gerar_hash_senha, verificar_senha
from app.database import get_db
from app.models import User
from app.models.enums import AuditAction, EntityType, Role
from app.models.tenant import Tenant, TenantUser
from app.schemas import RegistroRequest, TokenResponse, UsuarioResponse
from app.services.audit import AuditService, get_audit_service

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


def _buscar_por_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(dados: RegistroRequest, db: Session = Depends(get_db)) -> User:
    """Cadastra um usuário."""
    # O e-mail é normalizado para minúsculas para que o login não dependa de
    # como o usuário digitou no cadastro.
    email = dados.email.lower().strip()

    if _buscar_por_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail.",
        )

    try:
        senha_hash = gerar_hash_senha(dados.senha)
    except SenhaMuitoLongaError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    usuario = User(email=email, nome=dados.nome.strip(), senha_hash=senha_hash)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    audit: AuditService = Depends(get_audit_service),
) -> TokenResponse:
    """
    Autentica e devolve o token.

    Usa formulário em vez de JSON porque é o que o padrão OAuth2 define e o que
    faz o botão Authorize do /docs funcionar — útil para demonstrar a API sem a
    interface. O campo `username` recebe o e-mail.
    """
    usuario = _buscar_por_email(db, form.username.lower().strip())

    # A mesma mensagem para e-mail inexistente e senha errada, de propósito:
    # distinguir os dois casos revelaria quais e-mails estão cadastrados.
    if usuario is None or not verificar_senha(form.password, usuario.senha_hash):
        audit.log_action(
            action=AuditAction.LOGIN_FAILURE,
            actor_user_id=usuario.id if usuario else None,
            entity_type=EntityType.USER,
            entity_id=str(usuario.id) if usuario else None,
            metadata_info={"email_tentativa": form.username.lower().strip()}
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    audit.log_action(
        action=AuditAction.LOGIN_SUCCESS,
        actor_user_id=usuario.id,
        entity_type=EntityType.USER,
        entity_id=str(usuario.id)
    )
    db.commit()
    return TokenResponse(
        access_token=criar_token(usuario.id, usuario.email),
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.get("/eu", response_model=UsuarioResponse)
def eu(usuario: User = Depends(usuario_atual)) -> User:
    """Devolve o usuário do token. Serve para o frontend validar a sessão."""
    return usuario





@router.get("/sso/login")
def sso_login(domain: str, db: Session = Depends(get_db)) -> dict[str, str]:
    tenant = db.scalar(select(Tenant).where(Tenant.domain == domain))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado para este domínio")
    return {"redirect_url": f"https://sso.provider.com/auth?domain={domain}"}

@router.get("/sso/callback", response_model=TokenResponse)
def sso_callback(email: str, db: Session = Depends(get_db), audit: AuditService = Depends(get_audit_service)) -> TokenResponse:
    domain = email.split('@')[-1]
    tenant = db.scalar(select(Tenant).where(Tenant.domain == domain))
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não configurado")

    usuario = _buscar_por_email(db, email)
    if not usuario:
        usuario = User(email=email, nome=email.split('@')[0], senha_hash="SSO_MANAGED")
        db.add(usuario)
        db.flush()
        tu = TenantUser(tenant_id=tenant.id, user_id=usuario.id, role=Role.DEVELOPER)
        db.add(tu)

    audit.log_action(
        action=AuditAction.LOGIN_SUCCESS,
        actor_user_id=usuario.id,
        entity_type=EntityType.USER,
        entity_id=str(usuario.id),
        metadata_info={"sso": True, "tenant": tenant.domain}
    )
    db.commit()

    return TokenResponse(
        access_token=criar_token(usuario.id, usuario.email),
        usuario=UsuarioResponse.model_validate(usuario),
    )
