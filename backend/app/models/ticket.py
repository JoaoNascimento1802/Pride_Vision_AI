from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TicketProvider, TicketStatus

if TYPE_CHECKING:
    from app.models.vulnerability import Vulnerability


class Ticket(Base):
    """
    Rastreamento de um ticket criado em sistema externo (Jira, GitHub, etc)
    para remediação de uma vulnerabilidade.
    """

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    vulnerabilidade_id: Mapped[int] = mapped_column(
        ForeignKey("vulnerabilidades.id", ondelete="CASCADE"), index=True
    )

    # Provider
    provider: Mapped[TicketProvider] = mapped_column(
        SAEnum(TicketProvider, native_enum=False, values_callable=lambda e: [m.value for m in e])
    )

    # Identificadores externos
    external_id: Mapped[str] = mapped_column(String(100))
    external_key: Mapped[str | None] = mapped_column(String(100), default=None)
    url: Mapped[str] = mapped_column(String(500))

    # Informações do Ticket
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[TicketStatus] = mapped_column(
        SAEnum(TicketStatus, native_enum=False, values_callable=lambda e: [m.value for m in e]),
        default=TicketStatus.OPEN,
    )

    # Controle
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    # Relacionamento
    vulnerabilidade: Mapped[Vulnerability] = relationship(back_populates="tickets")

    def __repr__(self) -> str:
        return f"<Ticket {self.provider.value} {self.external_key or self.external_id}>"
