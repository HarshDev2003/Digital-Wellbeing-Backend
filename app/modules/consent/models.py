"""SQLAlchemy ORM model for explicit User Consent logging."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserConsent(Base):
    """Audit log of explicit user consent actions."""
    __tablename__ = "user_consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consent_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 'USAGE_COLLECTION', 'AI_ANALYSIS'
    policy_version: Mapped[str] = mapped_column(String(32), nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="consents")
