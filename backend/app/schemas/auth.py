# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
auth.py — Schemas de entrada e saída da autenticação.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, model_validator

from app.auth.security import SENHA_MAX_BYTES


class RegistroRequest(BaseModel):
    """Cadastro de um novo usuário."""
    email: EmailStr
    nome: str = Field(min_length=2, max_length=120)
    senha: str = Field(min_length=8, max_length=SENHA_MAX_BYTES)


class UsuarioResponse(BaseModel):
    """Usuário devolvido pela API. Nunca inclui o hash da senha."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nome: str
    criado_em: datetime
    role: str

    @computed_field
    @property
    def permissions(self) -> list[str]:
        from app.auth.rbac import get_permissions
        from app.models.enums import Role
        return get_permissions(Role(self.role))

    tenants: list[dict[str, str | int]] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def extract_tenants(cls, data: Any) -> Any:
        if hasattr(data, "tenant_users"):
            tenants = []
            for tu in data.tenant_users:
                if getattr(tu, "tenant", None):
                    tenants.append({"id": tu.tenant.id, "name": tu.tenant.name})
            if not tenants:
                tenants = [{"id": 1, "name": "Default Organization"}]
            
            return {
                "id": data.id,
                "email": data.email,
                "nome": data.nome,
                "criado_em": data.criado_em,
                "role": data.role.value if hasattr(data.role, "value") else data.role,
                "tenants": tenants
            }
        return data


class TokenResponse(BaseModel):
    """Resposta do login."""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse