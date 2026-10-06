# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
integration.py — Armazenamento seguro de credenciais e integrações OAuth.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.user import User


class Integration(Base):
    """
    Representa uma integração externa configurada para a plataforma ou usuário.
    Tokens não devem ser inseridos em texto puro.
    """
    __tablename__ = "integrations"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, default=1)

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)  # ex: 'jira'
    user_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)

    cloud_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Credenciais criptografadas
    access_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Controle de expiração do access token
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    user: Mapped[User] = relationship()

    def __repr__(self) -> str:
        return f"<Integration {self.id} {self.provider}>"

