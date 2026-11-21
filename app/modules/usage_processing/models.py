"""SQLAlchemy ORM models for Daily Usage Summaries and App Breakdowns."""
import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DailyUsageSummary(Base):
    """Aggregated daily device usage summary in user local timezone."""
    __tablename__ = "daily_usage_summaries"

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
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    calendar_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_screen_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_unlocks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "device_id", "calendar_date", name="uq_daily_summary_user_device_date"),
        Index("idx_daily_summaries_user_date", "user_id", "calendar_date"),
    )

    # Relationships
    user = relationship("User")
    device = relationship("Device")
    app_summaries = relationship(
        "AppDailySummary",
        back_populates="daily_summary",
        cascade="all, delete-orphan",
    )


class AppDailySummary(Base):
    """Per-application foreground allocation within a daily summary."""
    __tablename__ = "app_daily_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    daily_summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_usage_summaries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_foreground_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    session_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("daily_summary_id", "package_name", name="uq_app_daily_summary_pkg"),
    )

    # Relationships
    daily_summary = relationship("DailyUsageSummary", back_populates="app_summaries")
