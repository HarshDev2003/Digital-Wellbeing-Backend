"""SQLAlchemy ORM models for Usage Goals, App Limits, and Violation auditing."""
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AppCategory(Base):
    """System catalog of application functional categories."""
    __tablename__ = "app_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False)


class UsageGoal(Base):
    """User-defined goal for daily screen time or category limits."""
    __tablename__ = "usage_goals"

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
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)  # 'TOTAL_SCREEN_TIME' or 'CATEGORY'
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("app_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    max_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user = relationship("User")
    category = relationship("AppCategory")


class AppLimit(Base):
    """Daily duration threshold configured for an individual application."""
    __tablename__ = "app_limits"

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
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "package_name", name="uq_user_app_limit_pkg"),
    )

    # Relationships
    user = relationship("User")


class AppLimitViolation(Base):
    """Historical audit log of limit breaches."""
    __tablename__ = "app_limit_violations"

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
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    violation_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    limit_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user = relationship("User")
    device = relationship("Device")
