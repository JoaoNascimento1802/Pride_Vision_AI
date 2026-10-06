# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""
policy.py — Políticas de segurança e exceções do Security Gate.

Uma Policy define uma regra que deve ser avaliada antes de um deploy/merge.
Pode ser global (aplicacao_id=None) ou específica para uma aplicação.

Uma PolicyException permite que uma violação conhecida seja ignorada
temporariamente, desde que não tenha expirado e esteja aprovada.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import GateDecision, Risco

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User
    from app.models.vulnerability import Vulnerability


class Policy(Base):
    """
    Política de segurança avaliada pelo Security Gate.

    O campo `condicao` armazena a lógica da regra em formato simples:
      - risco_minimo: nível mínimo de risco que aciona a política (ex: "critico")
      - acao: decisão que a política impõe (BLOCK, WARN, PASS)

    Uma policy sem aplicacao_id é global (vale para todas as aplicações).
    Uma policy com aplicacao_id vale apenas para aquela aplicação.

    Quando múltiplas políticas incidem sobre um finding, a mais restritiva vence.
    """

    __tablename__ = "policies"

    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, default=1)

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int | None] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True, default=None
    )
    nome: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(Text, default=None)

    # Nível mínimo de risco que aciona esta política (aplica-se a descobertas normais)
    risco_minimo: Mapped[Risco] = mapped_column(
        SAEnum(Risco, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=Risco.CRITICO,
    )

    # Supply Chain Policy rules
    require_signature: Mapped[bool] = mapped_column(default=False)
    require_provenance: Mapped[bool] = mapped_column(default=False)
    trusted_builder: Mapped[str | None] = mapped_column(String(255), default=None)


    # Ação tomada quando a política é violada
    acao: Mapped[GateDecision] = mapped_column(
        SAEnum(GateDecision, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=GateDecision.BLOCK,
    )

    ativa: Mapped[bool] = mapped_column(default=True)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    aplicacao: Mapped[Application | None] = relationship()
    excecoes: Mapped[list[PolicyException]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        scope = f"app={self.aplicacao_id}" if self.aplicacao_id else "global"
        return f"<Policy {self.id} [{scope}] {self.nome} → {self.acao.value}>"


class PolicyException(Base):
    """
    Exceção temporária para uma violação de política específica.

    Permite que um finding com vulnerabilidade conhecida não bloqueie um
    pipeline enquanto a correção está em andamento, desde que:
      - a exceção esteja aprovada
      - a data de expiração não tenha passado

    Após a expiração, a política volta a ser aplicada normalmente.
    """

    __tablename__ = "policy_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(
        ForeignKey("policies.id", ondelete="CASCADE"), index=True
    )
    vulnerabilidade_id: Mapped[int] = mapped_column(
        ForeignKey("vulnerabilidades.id", ondelete="CASCADE"), index=True
    )

    justificativa: Mapped[str] = mapped_column(Text)
    aprovado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), default=None
    )
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    policy: Mapped[Policy] = relationship(back_populates="excecoes")
    vulnerabilidade: Mapped[Vulnerability] = relationship()
    aprovado_por: Mapped[User | None] = relationship()

    @property
    def valida(self) -> bool:
        """True se a exceção ainda não expirou."""
        if self.expira_em is None:
            return True  # exceção permanente (sem data de expiração)
        # SQLite pode retornar datetime sem tzinfo; comparar de forma segura
        agora = datetime.now(UTC)
        expira = self.expira_em
        if expira.tzinfo is None:
            # naive → comparar sem tz
            agora = agora.replace(tzinfo=None)
        return agora < expira

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PolicyException {self.id} policy={self.policy_id} "
            f"vuln={self.vulnerabilidade_id} expira={self.expira_em}>"
        )
