"""Pydantic schemas for Telemetry Usage Ingestion."""
import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class ScreenEventItem(BaseModel):
    """Atomic screen activity event."""
    event_uuid: uuid.UUID
    event_type: str = Field(..., pattern="^(SCREEN_ON|SCREEN_OFF|USER_UNLOCKED)$")
    timestamp: datetime


class AppUsageEventItem(BaseModel):
    """Atomic foreground app usage interval."""
    event_uuid: uuid.UUID
    package_name: str = Field(..., max_length=255)
    start_time: datetime
    end_time: datetime
    duration_seconds: int = Field(..., ge=0)


class UsageSyncRequest(BaseModel):
    """Batch synchronization payload uploaded by mobile companion."""
    device_id: uuid.UUID
    sync_batch_id: uuid.UUID
    screen_events: List[ScreenEventItem] = Field(default_factory=list)
    app_events: List[AppUsageEventItem] = Field(default_factory=list)


class UsageSyncResponse(BaseModel):
    """Server confirmation of processed and ignored duplicate telemetry records."""
    status: str = "success"
    sync_batch_id: uuid.UUID
    processed_events: int
    duplicate_events_ignored: int
    server_timestamp: datetime
