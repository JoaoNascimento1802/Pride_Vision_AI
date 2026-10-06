# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.application import Application

class CloudAccount(Base):
    """
    Uma conta na nuvem (ex: AWS Account ID, GCP Project ID, Azure Subscription ID).
    """
    __tablename__ = "cloud_accounts"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, default=1)

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), index=True)
    account_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    alias: Mapped[str | None] = mapped_column(String(200), default=None)


class CloudResource(Base):
    """
    Um recurso de infraestrutura na nuvem (ex: S3 Bucket, EC2, IAM Role).
    """
    __tablename__ = "cloud_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    cloud_account_id: Mapped[int] = mapped_column(ForeignKey("cloud_accounts.id", ondelete="CASCADE"), index=True)
    arn_or_uri: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    resource_type: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100))

    # Relacionamento opcional com Application (para Toxic Combinations)
    aplicacao_id: Mapped[int | None] = mapped_column(ForeignKey("aplicacoes.id", ondelete="SET NULL"), index=True, default=None)

    cloud_account: Mapped[CloudAccount] = relationship()
    # A aplicacao que roda neste recurso, permitindo correlacao Code to Cloud
    aplicacao: Mapped["Application"] = relationship()
