# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
user.py — Usuário da plataforma.

Login simples com controle de acesso baseado em papéis (RBAC). Todo usuário
com permissão de leitura enxerga todas as aplicações.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Role
from app.models.tenant import TenantUser


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(120))
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=Role.DEVELOPER,
    )

    # Hash bcrypt. A senha em texto nunca é armazenada nem registrada em log.
    senha_hash: Mapped[str] = mapped_column(String(255))

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    tenant_users: Mapped[list[TenantUser]] = relationship()

    def __repr__(self) -> str:  # pragma: no cover — auxílio de depuração
        return f"<User {self.id} {self.email}>"
