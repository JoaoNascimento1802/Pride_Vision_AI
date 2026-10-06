# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Role


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(120), unique=True, index=True)
    sso_config: Mapped[dict[str, str] | None] = mapped_column(JSON)

    users: Mapped[list[TenantUser]] = relationship(back_populates="tenant")

class TenantUser(Base):
    __tablename__ = "tenant_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=Role.DEVELOPER,
    )

    tenant: Mapped[Tenant] = relationship(back_populates="users")
