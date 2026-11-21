"""Pydantic schemas for Analytics Overview & History endpoints."""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class HeadlineMetrics(BaseModel):
    """Headline metrics for the overview card."""
    total_screen_time_seconds: int = 0
    total_screen_time_formatted: str = "0m"
    total_unlocks: int = 0
    total_app_sessions: int = 0


class TopAppItem(BaseModel):
    """Ranked application breakdown item."""
    package_name: str
    display_name: str
    category: str = "Uncategorized"
    duration_seconds: int = 0
    duration_formatted: str = "0m"
    percentage_of_total: float = 0.0


class CategoryBreakdownItem(BaseModel):
    """Usage aggregated by functional category."""
    category: str
    duration_seconds: int = 0
    percentage: float = 0.0


class GoalsStatusOverview(BaseModel):
    """Status against active daily screen time target."""
    daily_goal_seconds: int
    consumed_seconds: int
    status: str = "ON_TRACK"  # 'ON_TRACK', 'EXCEEDED'


class NetworkTelemetryOverview(BaseModel):
    """Network consumption summary or platform restriction notice."""
    supported: bool = True
    platform_restricted: bool = False
    message: Optional[str] = None
    wifi_bytes_total: Optional[int] = None
    mobile_bytes_total: Optional[int] = None


class AnalyticsOverviewResponse(BaseModel):
    """Response payload for GET /api/v1/analytics/overview."""
    calendar_date: date
    timezone: str
    headline_metrics: HeadlineMetrics
    top_apps: List[TopAppItem] = Field(default_factory=list)
    category_breakdown: List[CategoryBreakdownItem] = Field(default_factory=list)
    goals_status: Optional[GoalsStatusOverview] = None
    network_telemetry: Optional[NetworkTelemetryOverview] = None


class HistoricalTrendItem(BaseModel):
    """Summary record for a single day in historical trends."""
    calendar_date: date
    total_screen_time_seconds: int = 0
    total_unlocks: int = 0
    top_category: str = "General"
    goal_met: bool = True


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int
    page_size: int
    total_records: int
    total_pages: int


class AnalyticsHistoryResponse(BaseModel):
    """Response payload for GET /api/v1/analytics/history."""
    start_date: date
    end_date: date
    pagination: PaginationInfo
    items: List[HistoricalTrendItem] = Field(default_factory=list)
