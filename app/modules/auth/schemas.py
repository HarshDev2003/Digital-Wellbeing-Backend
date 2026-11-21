"""Pydantic schemas for Authentication endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload for user account registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")
    timezone: str = Field(default="UTC", description="IANA Timezone, e.g. 'America/New_York'")


class UserRegisterResponse(BaseModel):
    """Response returned upon successful user registration."""
    user_id: uuid.UUID
    email: EmailStr
    timezone: str
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900


class UserLoginRequest(BaseModel):
    """Payload for user login."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Response returned upon successful user login."""
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    """Payload to refresh an expired access token."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token refresh response."""
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 900


class UserResponse(BaseModel):
    """User profile response."""
    id: uuid.UUID
    email: EmailStr
    timezone: str
    is_active: bool
    created_at: datetime
