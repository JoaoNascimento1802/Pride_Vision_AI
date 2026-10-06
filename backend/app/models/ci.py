# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
ci.py — Modelos para rastreamento de pipelines de CI/CD e histórico de Security Gates.

PipelineRun: representa uma execução de pipeline que acionou o Security Gate.
SecurityGateResult: o resultado determinístico (PASS/WARN/BLOCK) de uma avaliação.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Ambiente, GateDecision

if TYPE_CHECKING:
    from app.models.application import Application


class PipelineRun(Base):
    """
    Representa uma execução de pipeline que acionou o Security Gate.

    A tripla (aplicacao_id, pipeline_id, commit_sha) identifica uma execução
    única — chamadas repetidas reencontram o registro em vez de duplicar.

    Os campos opcionais (branch, run_id, provider) são preenchidos quando
    disponíveis no payload da chamada de CI/CD.
    """

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )

    # Identificadores do pipeline (ao menos um deve estar presente)
    provider: Mapped[str | None] = mapped_column(
        String(50), default=None
    )  # github, gitlab, jenkins…
    pipeline_id: Mapped[str | None] = mapped_column(String(255), default=None)
    run_id: Mapped[str | None] = mapped_column(String(255), default=None)
    commit_sha: Mapped[str | None] = mapped_column(String(255), index=True, default=None)
    branch: Mapped[str | None] = mapped_column(String(255), default=None)
    ambiente: Mapped[Ambiente | None] = mapped_column(
        SAEnum(Ambiente, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=None,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    aplicacao: Mapped[Application] = relationship()
    gate_results: Mapped[list[SecurityGateResult]] = relationship(
        back_populates="pipeline_run",
        cascade="all, delete-orphan",
        order_by="SecurityGateResult.avaliado_em.desc()",
    )

    @property
    def ultimo_resultado(self) -> SecurityGateResult | None:
        """Resultado mais recente do gate para este pipeline."""
        return self.gate_results[0] if self.gate_results else None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PipelineRun {self.id} app={self.aplicacao_id} "
            f"commit={self.commit_sha!r} provider={self.provider}>"
        )


class SecurityGateResult(Base):
    """
    Resultado determinístico de uma avaliação do Security Gate.

    Preservado como histórico: cada reavaliação (por novo scan, nova política,
    nova exceção) cria um novo registro sem apagar os anteriores. Isso
    alimenta auditoria e métricas ao longo do tempo.
    """

    __tablename__ = "security_gate_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_run_id: Mapped[int] = mapped_column(
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"), index=True
    )

    decision: Mapped[GateDecision] = mapped_column(
        SAEnum(GateDecision, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        index=True,
    )

    # Resumo textual da decisão (para exibição no PR/MR e na interface)
    reason: Mapped[str] = mapped_column(Text)

    # JSON serializado das políticas violadas e findings envolvidos
    # (mantido como texto para não exigir tabela auxiliar no MVP)
    policies_violated_json: Mapped[str | None] = mapped_column(Text, default=None)
    findings_json: Mapped[str | None] = mapped_column(Text, default=None)

    # Contadores para queries rápidas no dashboard
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    total_violations: Mapped[int] = mapped_column(Integer, default=0)

    avaliado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    pipeline_run: Mapped[PipelineRun] = relationship(back_populates="gate_results")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SecurityGateResult {self.id} "
            f"run={self.pipeline_run_id} decision={self.decision.value}>"
        )
