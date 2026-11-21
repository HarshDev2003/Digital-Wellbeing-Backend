"""Pydantic schemas for User Consent recording."""
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class UserConsentRequest(BaseModel):
    """Payload to grant or revoke explicit consent."""
    consent_type: str = Field(..., max_length=64, description="e.g. 'USAGE_COLLECTION', 'AI_ANALYSIS'")
    policy_version: str = Field(..., max_length=32, description="e.g. '1.0'")
    granted: bool = Field(..., description="True if granted, False if revoked")


class UserConsentResponse(BaseModel):
    """Response returned upon recording user consent."""
    status: str = "recorded"
    consent_id: uuid.UUID
    timestamp: datetime
