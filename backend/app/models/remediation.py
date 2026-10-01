"""
remediation.py — Modelos de comentários e evidências de remediação.

Comentários permitem que a equipe registre notas durante o ciclo de correção.
Evidências registram proof-of-fix: commit SHA, PR, referência externa, etc.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vulnerability import Vulnerability


class RemediationComment(Base):
    """
    Comentário de remediação vinculado a uma vulnerabilidade.

    Imutável: não há endpoint de edição/remoção.
    O autor é sempre o usuário autenticado que fez a requisição.
    """

    __tablename__ = "remediation_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    vulnerability_id: Mapped[int] = mapped_column(
        ForeignKey("vulnerabilidades.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), default=None
    )

    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    vulnerability: Mapped[Vulnerability] = relationship(back_populates="comments")
    author: Mapped[User | None] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RemediationComment {self.id} vuln={self.vulnerability_id}>"


class RemediationEvidence(Base):
    """
    Evidência de correção vinculada a uma vulnerabilidade.

    Exemplos: commit SHA, PR URL, resultado de re-scan, descrição textual.
    Não armazenar segredos, senhas ou tokens.
    """

    __tablename__ = "remediation_evidences"

    id: Mapped[int] = mapped_column(primary_key=True)
    vulnerability_id: Mapped[int] = mapped_column(
        ForeignKey("vulnerabilidades.id", ondelete="CASCADE"), index=True
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), default=None
    )

    evidence_type: Mapped[str] = mapped_column(
        String(50), default="other"
    )  # commit, pr, scan, description, other
    description: Mapped[str] = mapped_column(Text)
    reference: Mapped[str | None] = mapped_column(String(500), default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    vulnerability: Mapped[Vulnerability] = relationship(back_populates="evidences")
    author: Mapped[User | None] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RemediationEvidence {self.id} type={self.evidence_type} vuln={self.vulnerability_id}>"

