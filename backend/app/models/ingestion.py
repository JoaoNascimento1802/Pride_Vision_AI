# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ingestion.py — Uploads e achados brutos.

Um `Upload` é um arquivo enviado; um `Finding` é uma linha desse arquivo já
normalizada para o formato comum do PRIDE. Os achados são preservados
individualmente mesmo depois de correlacionados, porque a tela de detalhes
precisa mostrar o que cada ferramenta reportou separadamente.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Ferramenta

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.vulnerability import Vulnerability

_ENUM_FERRAMENTA = SAEnum(
    Ferramenta, native_enum=False, values_callable=lambda e: [m.value for m in e]
)


class Upload(Base):
    """Registro de um arquivo de relatório enviado para uma aplicação."""

    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )

    ferramenta: Mapped[Ferramenta] = mapped_column(_ENUM_FERRAMENTA)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    tamanho_bytes: Mapped[int] = mapped_column(Integer)

    # Quantos achados o arquivo produziu e quantos foram descartados por estarem
    # malformados. Exibir os dois números evita a impressão de que o upload
    # falhou silenciosamente quando o relatório tinha lixo.
    total_achados: Mapped[int] = mapped_column(Integer, default=0)
    total_ignorados: Mapped[int] = mapped_column(Integer, default=0)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    aplicacao: Mapped[Application] = relationship(back_populates="uploads")
    achados: Mapped[list[Finding]] = relationship(
        back_populates="upload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover — auxílio de depuração
        return f"<Upload {self.id} {self.ferramenta.value} {self.nome_arquivo}>"


class Finding(Base):
    """
    Um achado individual, já normalizado.

    Os campos espelham o que a especificação manda extrair de cada ferramenta:
    do Semgrep vêm regra, arquivo, linha, mensagem, severidade e CWE; do Nuclei
    vêm template, tipo, severidade, URL, endpoint, status HTTP e evidência.
    """

    __tablename__ = "achados"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )
    upload_id: Mapped[int | None] = mapped_column(ForeignKey("uploads.id", ondelete="CASCADE"), index=True, default=None)
    vulnerabilidade_id: Mapped[int | None] = mapped_column(
        ForeignKey("vulnerabilidades.id", ondelete="CASCADE"), index=True, default=None
    )

    # --- Campos comuns às duas ferramentas ---
    origem: Mapped[Ferramenta] = mapped_column(_ENUM_FERRAMENTA)
    tipo_vuln: Mapped[str] = mapped_column(String(120), index=True)
    endpoint: Mapped[str] = mapped_column(String(500), index=True)
    severidade: Mapped[str] = mapped_column(String(40))
    mensagem: Mapped[str] = mapped_column(Text)
    regra_id: Mapped[str] = mapped_column(String(300))

    # --- Somente Semgrep ---
    arquivo: Mapped[str | None] = mapped_column(String(500), default=None)
    linha: Mapped[int | None] = mapped_column(Integer, default=None)

    # --- Somente Runtime (eBPF) ---
    process_name: Mapped[str | None] = mapped_column(String(255), default=None)
    pid: Mapped[int | None] = mapped_column(Integer, default=None)
    syscall: Mapped[str | None] = mapped_column(String(100), default=None)
    container_id: Mapped[str | None] = mapped_column(String(255), index=True, default=None)


    # --- Somente Cloud CSPM ---
    cloud_provider: Mapped[str | None] = mapped_column(String(50), default=None)
    region: Mapped[str | None] = mapped_column(String(50), default=None)
    compliance_control: Mapped[str | None] = mapped_column(String(200), default=None)

    hit_count: Mapped[int] = mapped_column(Integer, default=1)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    cwe: Mapped[str | None] = mapped_column(String(300), default=None)

    # --- Somente Nuclei ---
    url: Mapped[str | None] = mapped_column(String(1000), default=None)
    http_status: Mapped[int | None] = mapped_column(Integer, default=None)
    evidencia: Mapped[str | None] = mapped_column(Text, default=None)

    # --- Somente Gitleaks / Secrets ---
    repository: Mapped[str | None] = mapped_column(String(255), default=None)
    commit: Mapped[str | None] = mapped_column(String(255), default=None)
    fingerprint: Mapped[str | None] = mapped_column(String(255), default=None)

    # --- Somente IaC ---
    resource: Mapped[str | None] = mapped_column(String(500), default=None)
    resource_type: Mapped[str | None] = mapped_column(String(200), default=None)
    iac_provider: Mapped[str | None] = mapped_column(String(100), default=None)
    framework: Mapped[str | None] = mapped_column(String(100), default=None)
    guideline: Mapped[str | None] = mapped_column(Text, default=None)

    # --- Somente Container ---
    container_image_id: Mapped[int | None] = mapped_column(
        ForeignKey("container_images.id", ondelete="CASCADE"), index=True, default=None
    )
    layer: Mapped[str | None] = mapped_column(String(255), default=None)
    pacote: Mapped[str | None] = mapped_column(String(255), default=None)
    versao: Mapped[str | None] = mapped_column(String(100), default=None)
    versao_corrigida: Mapped[str | None] = mapped_column(String(100), default=None)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    upload: Mapped[Upload] = relationship(back_populates="achados")
    vulnerabilidade: Mapped[Vulnerability | None] = relationship(back_populates="achados")
    container_image = relationship("ContainerImage")

    @property
    def image_name(self) -> str | None:
        return self.container_image.name if self.container_image else None

    @property
    def image_repository(self) -> str | None:
        return self.container_image.name if self.container_image else None

    @property
    def image_tag(self) -> str | None:
        return self.container_image.tag if self.container_image else None

    @property
    def image_digest(self) -> str | None:
        return self.container_image.digest if self.container_image else None

    @property
    def os(self) -> str | None:
        return self.container_image.os if self.container_image else None

    @property
    def architecture(self) -> str | None:
        return self.container_image.architecture if self.container_image else None

    @property
    def registry_name(self) -> str | None:
        return self.container_image.registry_name if self.container_image else None

    @property
    def base_image(self) -> str | None:
        return self.container_image.base_image if self.container_image else None

    def __repr__(self) -> str:  # pragma: no cover — auxílio de depuração
        return f"<Finding {self.id} {self.origem.value} {self.tipo_vuln}@{self.endpoint}>"
