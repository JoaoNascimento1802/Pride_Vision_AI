# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApiAsset(Base):
    __tablename__ = "api_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True)
    nome: Mapped[str] = mapped_column(String(255))
    base_url: Mapped[str] = mapped_column(String(255))
    spec_url: Mapped[str] = mapped_column(String(255))

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    id: Mapped[int] = mapped_column(primary_key=True)
    api_asset_id: Mapped[int] = mapped_column(ForeignKey("api_assets.id", ondelete="CASCADE"), index=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(255))
