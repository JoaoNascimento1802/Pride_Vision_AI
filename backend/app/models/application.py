# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
application.py — Inventário de aplicações.

É a parte do ASPM que dá contexto de negócio ao risco: a mesma falha vale mais
em produção exposta à internet do que num ambiente de teste interno.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Ambiente, Exposicao, Importancia

if TYPE_CHECKING:
    from app.models.container import ContainerImage
    from app.models.ingestion import Upload
    from app.models.sbom import Sbom
    from app.models.vulnerability import Vulnerability


class Application(Base):
    __tablename__ = "aplicacoes"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, default=1)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), index=True)
    responsavel: Mapped[str] = mapped_column(String(160))
    url: Mapped[str | None] = mapped_column(String(500), default=None)

    # Os três fatores de contexto que entram na matriz de risco.
    # native_enum=False guarda como VARCHAR com CHECK, o que é portável entre
    # SQLite e Postgres caso a hospedagem exija a troca.
    ambiente: Mapped[Ambiente] = mapped_column(
        SAEnum(Ambiente, native_enum=False, values_callable=lambda e: [m.value for m in e])
    )
    exposicao: Mapped[Exposicao] = mapped_column(
        SAEnum(Exposicao, native_enum=False, values_callable=lambda e: [m.value for m in e])
    )
    importancia: Mapped[Importancia] = mapped_column(
        SAEnum(Importancia, native_enum=False, values_callable=lambda e: [m.value for m in e])
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Apagar a aplicação apaga o que veio dela — não faz sentido manter
    # vulnerabilidades órfãs de uma aplicação removida do inventário.
    uploads: Mapped[list[Upload]] = relationship(
        back_populates="aplicacao", cascade="all, delete-orphan"
    )
    vulnerabilidades: Mapped[list[Vulnerability]] = relationship(
        back_populates="aplicacao", cascade="all, delete-orphan"
    )
    sboms: Mapped[list[Sbom]] = relationship(
        back_populates="aplicacao", cascade="all, delete-orphan"
    )
    container_images: Mapped[list[ContainerImage]] = relationship(
        back_populates="aplicacao", cascade="all, delete-orphan"
    )

    @property
    def critica_para_o_negocio(self) -> bool:
        """
        True quando a aplicação é exposta à internet ou tem alta importância.

        É exatamente o fator que a especificação usa para separar Crítico de
        Alto quando as duas ferramentas confirmam algo em produção.
        """
        return self.exposicao is Exposicao.INTERNET or self.importancia is Importancia.ALTA

    def __repr__(self) -> str:  # pragma: no cover — auxílio de depuração
        return f"<Application {self.id} {self.nome} ({self.ambiente.value})>"
