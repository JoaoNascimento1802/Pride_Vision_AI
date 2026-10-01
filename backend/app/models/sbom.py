from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.application import Application


class Sbom(Base):
    """
    Registro de um Software Bill of Materials associado a uma aplicação.
    """

    __tablename__ = "sboms"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )

    formato: Mapped[str] = mapped_column(String(50))  # cyclonedx, spdx
    versao_formato: Mapped[str | None] = mapped_column(String(50), default=None)

    # Historico e rastreabilidade
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    tamanho_bytes: Mapped[int] = mapped_column(Integer)

    # Metadata opcional extraido do documento
    serial_number: Mapped[str | None] = mapped_column(String(255), default=None)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    aplicacao: Mapped[Application] = relationship(back_populates="sboms")
    componentes: Mapped[list[SbomComponent]] = relationship(
        back_populates="sbom", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Sbom {self.id} {self.formato} app={self.aplicacao_id}>"


class SbomComponent(Base):
    """
    Um componente listado dentro de um SBOM.
    """

    __tablename__ = "sbom_componentes"

    id: Mapped[int] = mapped_column(primary_key=True)
    sbom_id: Mapped[int] = mapped_column(ForeignKey("sboms.id", ondelete="CASCADE"), index=True)

    nome: Mapped[str] = mapped_column(String(255), index=True)
    versao: Mapped[str | None] = mapped_column(String(100), default=None, index=True)
    ecossistema: Mapped[str | None] = mapped_column(String(100), default=None)

    tipo_componente: Mapped[str | None] = mapped_column(
        String(100), default=None
    )  # library, application, os

    # Identificadores padronizados
    purl: Mapped[str | None] = mapped_column(String(500), default=None, index=True)
    cpe: Mapped[str | None] = mapped_column(String(500), default=None)

    # Metadados de cadeia de suprimentos
    fornecedor: Mapped[str | None] = mapped_column(String(255), default=None)
    licenca: Mapped[str | None] = mapped_column(String(255), default=None)

    # Detalhes adicionais podem ser JSON ou Text
    hashes: Mapped[str | None] = mapped_column(Text, default=None)

    # Referência opcional à CVE caso o próprio SBOM traga (como faz o VEX)
    cve_relacionada: Mapped[str | None] = mapped_column(String(255), default=None)

    sbom: Mapped[Sbom] = relationship(back_populates="componentes")

    def __repr__(self) -> str:
        return f"<SbomComponent {self.nome}@{self.versao}>"
