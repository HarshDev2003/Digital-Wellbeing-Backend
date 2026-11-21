"""SQLAlchemy ORM models for Devices and Device Capabilities."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Device(Base):
    """Physical mobile device model running the companion collector."""
    __tablename__ = "devices"

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
    device_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)  # 'android' or 'ios'
    device_model: Mapped[str] = mapped_column(String(128), nullable=False)
    os_version: Mapped[str] = mapped_column(String(32), nullable=False)
    app_version: Mapped[str] = mapped_column(String(32), nullable=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "device_identifier", name="uq_user_device_identifier"),
    )

    # Relationships
    user = relationship("User", back_populates="devices")
    capabilities = relationship(
        "DeviceCapability",
        back_populates="device",
        uselist=False,
        cascade="all, delete-orphan",
    )


class DeviceCapability(Base):
    """Platform feature support and permission state per device."""
    __tablename__ = "device_capabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    supports_network_tracking: Mapped[bool] = mapped_column(Boolean, nullable=False)
    supports_app_shielding: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_usage_permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_screen_time_permission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    device = relationship("Device", back_populates="capabilities")
