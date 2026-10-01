from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ArtifactVerification(Base):
    """
    Registro da verificação de supply chain (assinatura, proveniência) de um artefato (como container image).
    """
    __tablename__ = "artifact_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    aplicacao_id: Mapped[int] = mapped_column(
        ForeignKey("aplicacoes.id", ondelete="CASCADE"), index=True
    )

    artifact_reference: Mapped[str] = mapped_column(String(255))
    artifact_digest: Mapped[str] = mapped_column(String(255), index=True)

    signature_present: Mapped[bool] = mapped_column(Boolean, default=False)
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False)

    signer_identity: Mapped[str | None] = mapped_column(String(255), default=None)
    certificate_issuer: Mapped[str | None] = mapped_column(String(255), default=None)

    attestation_present: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_present: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_valid: Mapped[bool] = mapped_column(Boolean, default=False)

    builder: Mapped[str | None] = mapped_column(String(255), default=None)
    source_repository: Mapped[str | None] = mapped_column(String(255), default=None)
    source_revision: Mapped[str | None] = mapped_column(String(255), default=None)

    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    verification_log: Mapped[str | None] = mapped_column(String, default=None)
