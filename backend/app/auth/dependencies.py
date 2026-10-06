# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import ler_token
from app.database import current_tenant_id, get_db
from app.models import User
from app.models.tenant import TenantUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou expiradas.",
    headers={"WWW-Authenticate": "Bearer"},
)

def usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    x_tenant_id: int | None = Header(None, alias="X-Tenant-ID"),
) -> User:
    usuario_id = ler_token(token)
    if usuario_id is None:
        raise CREDENCIAIS_INVALIDAS

    usuario = db.get(User, usuario_id)
    if usuario is None:
        raise CREDENCIAIS_INVALIDAS

    if x_tenant_id is not None:
        tu = db.query(TenantUser).filter_by(tenant_id=x_tenant_id, user_id=usuario.id).first()
        if tu is None:
            raise HTTPException(status_code=403, detail="Acesso negado a este Tenant")
        current_tenant_id.set(x_tenant_id)
        setattr(usuario, "current_role", tu.role)
    else:
        current_tenant_id.set(1)

    return usuario

class RequirePermission:
    def __init__(self, permission: str):
        self.permission = permission

    def __call__(self, user: User = Depends(usuario_atual)) -> User:
        from app.auth.rbac import get_permissions
        if self.permission not in get_permissions(getattr(user, "current_role", user.role)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: permissão insuficiente.",
            )
        return user
