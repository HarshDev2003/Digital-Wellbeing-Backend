"""Pydantic schemas for Goals and Limits endpoints."""
from datetime import date, datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class GoalCreateRequest(BaseModel):
    """Request payload to set a usage goal."""
    target_type: str = Field(..., pattern="^(TOTAL_SCREEN_TIME|CATEGORY)$")
    category_id: Optional[int] = None
    max_duration_seconds: int = Field(..., gt=0, description="Daily limit threshold in seconds")


class GoalResponse(BaseModel):
    """Response payload for a created or retrieved usage goal."""
    goal_id: uuid.UUID
    target_type: str
    category_id: Optional[int] = None
    max_duration_seconds: int
    is_active: bool


class GoalListResponse(BaseModel):
    """List of all configured usage goals for user."""
    goals: List[GoalResponse]


class AppLimitCreateRequest(BaseModel):
    """Request payload to configure an application duration limit."""
    package_name: str = Field(..., min_length=1, max_length=255)
    max_duration_seconds: int = Field(..., gt=0, description="Daily app limit threshold in seconds")


class AppLimitResponse(BaseModel):
    """Response payload for a configured app limit."""
    limit_id: uuid.UUID
    package_name: str
    max_duration_seconds: int
    is_active: bool


class AppLimitListResponse(BaseModel):
    """List of all active application limits for user."""
    limits: List[AppLimitResponse]


class ViolationItemResponse(BaseModel):
    """Item in historical violation log."""
    id: uuid.UUID
    package_name: str
    violation_date: date
    actual_duration_seconds: int
    limit_duration_seconds: int
    created_at: datetime


class ViolationListResponse(BaseModel):
    """List of logged limit breaches."""
    violations: List[ViolationItemResponse]
