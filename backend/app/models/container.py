# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.application import Application


class ContainerImage(Base):
    """
    Registro de uma imagem de container associada a uma aplicação.
    """
    __tablename__ = "container_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )

    repository: Mapped[str | None] = mapped_column(String(255), default=None)
    name: Mapped[str] = mapped_column(String(255))
    tag: Mapped[str | None] = mapped_column(String(100), default=None)
    digest: Mapped[str | None] = mapped_column(String(255), index=True, default=None)
    registry_name: Mapped[str | None] = mapped_column("registry", String(255), default=None)
    base_image: Mapped[str | None] = mapped_column(String(255), default=None)
    os: Mapped[str | None] = mapped_column(String(100), default=None)
    architecture: Mapped[str | None] = mapped_column(String(50), default=None)

    environment: Mapped[str | None] = mapped_column(String(50), default=None)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    aplicacao: Mapped[Application] = relationship(back_populates="container_images")

    def __repr__(self) -> str:
        return f"<ContainerImage {self.name}:{self.tag}@{self.digest}>"


class ContainerInstance(Base):
    """
    Representa uma instância em execução (Runtime) de um ContainerImage.
    Relaciona o 'container_id' do Docker/Kubernetes ao digest/imagem escaneada.
    """
    __tablename__ = "container_instances"

    id: Mapped[int] = mapped_column(primary_key=True)
    container_id: Mapped[str] = mapped_column(String(255), index=True, unique=True)

    container_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("container_images.id", ondelete="SET NULL"), index=True, default=None
    )

    namespace: Mapped[str | None] = mapped_column(String(100), default=None)
    pod_name: Mapped[str | None] = mapped_column(String(255), default=None)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    container_image: Mapped[ContainerImage | None] = relationship()

    def __repr__(self) -> str:
        return f"<ContainerInstance {self.container_id}>"
