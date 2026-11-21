"""Pydantic schemas for Telemetry Usage Ingestion."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ScreenEventItem(BaseModel):
    """Atomic screen activity event."""
    event_uuid: uuid.UUID
    event_type: str = Field(
        ...,
        pattern="^(SCREEN_ON|SCREEN_OFF|USER_UNLOCKED|SCREEN_UNLOCK)$",
    )
    timestamp: datetime

    @field_validator("event_type", mode="before")
    @classmethod
    def normalize_event_type(cls, v: str) -> str:
        """Map SCREEN_UNLOCK alias to USER_UNLOCKED."""
        if isinstance(v, str):
            clean = v.strip().upper()
            if clean == "SCREEN_UNLOCK":
                return "USER_UNLOCKED"
            return clean
        return v


class AppUsageEventItem(BaseModel):
    """Atomic foreground app usage interval."""
    event_uuid: uuid.UUID
    package_name: str = Field(..., max_length=255)
    start_time: datetime
    end_time: datetime
    duration_seconds: Optional[int] = Field(default=None, ge=0)

    @field_validator("duration_seconds", mode="after")
    @classmethod
    def calculate_duration(cls, v: Optional[int], info) -> int:
        """Derive duration_seconds if omitted by calculating end_time - start_time."""
        if v is not None:
            return v
        data = info.data
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end:
            return max(0, int((end - start).total_seconds()))
        return 0


class UsageSyncRequest(BaseModel):
    """Batch synchronization payload uploaded by mobile companion."""
    device_id: uuid.UUID
    sync_batch_id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    screen_events: List[ScreenEventItem] = Field(default_factory=list)
    app_events: List[AppUsageEventItem] = Field(default_factory=list)

    @field_validator("sync_batch_id", mode="before")
    @classmethod
    def default_sync_batch_id(cls, v: Optional[uuid.UUID]) -> uuid.UUID:
        if v is None:
            return uuid.uuid4()
        return v


class UsageSyncResponse(BaseModel):
    """Server confirmation of processed and ignored duplicate telemetry records."""
    status: str = "success"
    sync_batch_id: uuid.UUID
    processed_events: int
    duplicate_events_ignored: int
    server_timestamp: datetime
