"""Pydantic schemas for Device Registration and Capabilities."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DeviceCapabilitySchema(BaseModel):
    """Platform feature support flags for a device."""
    supports_network_tracking: bool = False
    supports_app_shielding: bool = False
    has_usage_permission: bool = False
    has_screen_time_permission: bool = False


class DeviceRegisterRequest(BaseModel):
    """Payload to register a physical companion device."""
    device_identifier: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Stable client UUID or hardware identifier",
    )
    platform: str = Field(
        default="android",
        description="'android', 'ios', or 'desktop'",
    )
    device_model: str = Field(default="Mobile Device", max_length=128)
    os_version: str = Field(default="Unknown", max_length=32)
    app_version: str = Field(default="1.0.0", max_length=32)
    capabilities: Optional[DeviceCapabilitySchema] = Field(
        default_factory=DeviceCapabilitySchema,
    )

    @field_validator("platform", mode="before")
    @classmethod
    def normalize_platform(cls, v: str) -> str:
        """Case-insensitive platform normalizer."""
        if isinstance(v, str):
            clean = v.strip().lower()
            if clean in ("android", "ios", "desktop"):
                return clean
        return "android"

    @field_validator("device_identifier", mode="before")
    @classmethod
    def default_device_identifier(cls, v: Optional[str]) -> str:
        """Assign auto-generated UUID string if device_identifier is missing or empty."""
        if not v or not str(v).strip():
            return str(uuid.uuid4())
        return str(v).strip()


class DeviceRegisterResponse(BaseModel):
    """Response returned upon successful device registration."""
    device_id: uuid.UUID
    status: str = "registered"
    registered_at: datetime


class DeviceItemResponse(BaseModel):
    """Device summary with capabilities."""
    id: uuid.UUID
    device_identifier: str
    platform: str
    device_model: str
    os_version: str
    app_version: str
    last_sync_at: Optional[datetime] = None
    capabilities: Optional[DeviceCapabilitySchema] = None


class DeviceListResponse(BaseModel):
    """List of all registered devices for the current user."""
    devices: List[DeviceItemResponse]
