"""Pydantic schemas for Device Registration and Capabilities."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DeviceCapabilitySchema(BaseModel):
    """Platform feature support flags for a device."""
    supports_network_tracking: bool
    supports_app_shielding: bool
    has_usage_permission: bool = False
    has_screen_time_permission: bool = False


class DeviceRegisterRequest(BaseModel):
    """Payload to register a physical companion device."""
    device_identifier: str = Field(..., max_length=128, description="Stable client UUID")
    platform: str = Field(..., pattern="^(android|ios)$", description="'android' or 'ios'")
    device_model: str = Field(..., max_length=128)
    os_version: str = Field(..., max_length=32)
    app_version: str = Field(..., max_length=32)
    capabilities: DeviceCapabilitySchema


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
