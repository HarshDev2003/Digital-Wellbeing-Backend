"""SQLAlchemy ORM models for Raw Telemetry Usage Ingestion."""
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AppUsageEvent(Base):
    """Raw foreground application usage interval received from a device."""
    __tablename__ = "app_usage_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("device_id", "event_uuid", name="uq_app_event_device_uuid"),
        Index("idx_app_events_device_time", "device_id", "start_time"),
        Index("idx_app_events_package", "package_name"),
    )

    # Relationships
    device = relationship("Device")


class ScreenActivityEvent(Base):
    """Raw physical device screen state transition (SCREEN_ON, SCREEN_OFF, USER_UNLOCKED)."""
    __tablename__ = "screen_activity_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("device_id", "event_uuid", name="uq_screen_event_device_uuid"),
        Index("idx_screen_events_device_time", "device_id", "timestamp"),
    )

    # Relationships
    device = relationship("Device")
