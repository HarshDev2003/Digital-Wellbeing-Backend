# API Contracts Specification: Digital Wellbeing Platform

**Base Path**: `/api/v1` | **Protocol**: HTTPS / REST / JSON | **Authentication**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`

---

## 1. Authentication Endpoints

### 1.1 Register User
- **POST** `/auth/register`
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "timezone": "America/New_York"
}
```
- **Response** (`201 Created`):
```json
{
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "user@example.com",
  "timezone": "America/New_York",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
  "token_type": "bearer",
  "expires_in_seconds": 900
}
```

### 1.2 Login User
- **POST** `/auth/login`
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
  "token_type": "bearer",
  "expires_in_seconds": 900,
  "refresh_token": "d290f1ee-6c54-4b01-90e6-d701748f0851"
}
```

---

## 2. Device Registration & Capabilities

### 2.1 Register Device
- **POST** `/devices/register`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "device_identifier": "550e8400-e29b-41d4-a716-446655440000",
  "platform": "android",
  "device_model": "Pixel 8",
  "os_version": "Android 14",
  "app_version": "1.0.0",
  "capabilities": {
    "supports_network_tracking": true,
    "supports_app_shielding": false,
    "has_usage_permission": true,
    "has_screen_time_permission": false
  }
}
```
- **Response** (`201 Created`):
```json
{
  "device_id": "c3a1b32d-289e-4e89-9134-8b1732a39201",
  "status": "registered",
  "registered_at": "2026-11-20T18:30:00Z"
}
```

---

## 3. Telemetry Ingestion Endpoints

### 3.1 Synchronize Usage Events (Idempotent)
- **POST** `/usage/sync`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "device_id": "c3a1b32d-289e-4e89-9134-8b1732a39201",
  "sync_batch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "screen_events": [
    {
      "event_uuid": "7a3b4c5d-0001-4000-8000-000000000001",
      "event_type": "SCREEN_ON",
      "timestamp": "2026-11-20T14:00:00Z"
    },
    {
      "event_uuid": "7a3b4c5d-0001-4000-8000-000000000002",
      "event_type": "USER_UNLOCKED",
      "timestamp": "2026-11-20T14:00:02Z"
    },
    {
      "event_uuid": "7a3b4c5d-0001-4000-8000-000000000003",
      "event_type": "SCREEN_OFF",
      "timestamp": "2026-11-20T14:35:00Z"
    }
  ],
  "app_events": [
    {
      "event_uuid": "8b4c5d6e-0002-4000-8000-000000000001",
      "package_name": "com.google.android.youtube",
      "start_time": "2026-11-20T14:00:05Z",
      "end_time": "2026-11-20T14:30:00Z",
      "duration_seconds": 1795
    }
  ]
}
```
- **Response** (`200 OK`):
```json
{
  "status": "success",
  "sync_batch_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "processed_events": 4,
  "duplicate_events_ignored": 0,
  "server_timestamp": "2026-11-20T18:35:00Z"
}
```

### 3.2 Synchronize Network Usage (Android Only)
- **POST** `/network/sync`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "device_id": "c3a1b32d-289e-4e89-9134-8b1732a39201",
  "calendar_date": "2026-11-20",
  "records": [
    {
      "event_uuid": "9c5d6e7f-0003-4000-8000-000000000001",
      "package_name": "com.google.android.youtube",
      "wifi_bytes_rx": 450201000,
      "wifi_bytes_tx": 12400000,
      "mobile_bytes_rx": 52400000,
      "mobile_bytes_tx": 2100000
    }
  ]
}
```
- **Response** (`200 OK`):
```json
{
  "status": "success",
  "processed_records": 1,
  "duplicate_records_ignored": 0
}
```

---

## 4. Analytics Endpoints

### 4.1 Dashboard Overview
- **GET** `/analytics/overview?date=2026-11-20&device_id=optional-uuid`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response** (`200 OK`):
```json
{
  "calendar_date": "2026-11-20",
  "timezone": "America/New_York",
  "headline_metrics": {
    "total_screen_time_seconds": 12600,
    "total_screen_time_formatted": "3h 30m",
    "total_unlocks": 42,
    "total_app_sessions": 68
  },
  "top_apps": [
    {
      "package_name": "com.google.android.youtube",
      "display_name": "YouTube",
      "category": "Entertainment",
      "duration_seconds": 5400,
      "duration_formatted": "1h 30m",
      "percentage_of_total": 42.8
    },
    {
      "package_name": "com.slack",
      "display_name": "Slack",
      "category": "Productivity",
      "duration_seconds": 3600,
      "duration_formatted": "1h 00m",
      "percentage_of_total": 28.5
    }
  ],
  "category_breakdown": [
    { "category": "Entertainment", "duration_seconds": 5400, "percentage": 42.8 },
    { "category": "Productivity", "duration_seconds": 3600, "percentage": 28.5 },
    { "category": "Social", "duration_seconds": 2400, "percentage": 19.0 },
    { "category": "Utilities", "duration_seconds": 1200, "percentage": 9.7 }
  ],
  "goals_status": {
    "daily_goal_seconds": 14400,
    "consumed_seconds": 12600,
    "status": "ON_TRACK"
  },
  "network_telemetry": {
    "supported": true,
    "platform_restricted": false,
    "wifi_bytes_total": 850400000,
    "mobile_bytes_total": 120500000
  }
}
```

*Note on iOS devices:*
```json
{
  "network_telemetry": {
    "supported": false,
    "platform_restricted": true,
    "message": "Per-app network telemetry is restricted by Apple operating system policies."
  }
}
```

### 4.2 Historical Usage Trends
- **GET** `/analytics/history?start_date=2026-11-01&end_date=2026-11-20&device_id=optional-uuid&page=1&page_size=20`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response** (`200 OK`):
```json
{
  "start_date": "2026-11-01",
  "end_date": "2026-11-20",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_records": 20,
    "total_pages": 1
  },
  "items": [
    {
      "calendar_date": "2026-11-20",
      "total_screen_time_seconds": 12600,
      "total_unlocks": 42,
      "top_category": "Entertainment",
      "goal_met": true
    }
  ]
}
```

---

## 5. Goals & Limits Endpoints

### 5.1 Set Screen Time Goal
- **POST** `/goals`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "target_type": "TOTAL_SCREEN_TIME",
  "max_duration_seconds": 14400
}
```
- **Response** (`201 Created`):
```json
{
  "goal_id": "1e2d3c4b-5a6f-7e8d-9c0b-1a2b3c4d5e6f",
  "target_type": "TOTAL_SCREEN_TIME",
  "max_duration_seconds": 14400,
  "is_active": true
}
```

### 5.2 Set Application Limit
- **POST** `/limits`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "package_name": "com.instagram.android",
  "max_duration_seconds": 2700
}
```
- **Response** (`201 Created`):
```json
{
  "limit_id": "2f3e4d5c-6b7a-8f9e-0d1c-2b3c4d5e6f7a",
  "package_name": "com.instagram.android",
  "max_duration_seconds": 2700,
  "is_active": true
}
```

---

## 6. AI Insights Endpoints

### 6.1 Generate AI Insights
- **POST** `/ai/insights/generate`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "timeframe": "WEEKLY",
  "start_date": "2026-11-14",
  "end_date": "2026-11-20"
}
```
- **Response** (`200 OK`):
```json
{
  "insight_id": "3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d",
  "title": "Healthy Productivity Spurt with Late-Night Spike",
  "wellbeing_score": 78,
  "summary": "Your screen time decreased by 12% this week with strong daytime productivity. However, entertainment usage spiked past 11:30 PM on Thursday and Friday.",
  "key_patterns": [
    "Late-night video streaming detected on 2 nights.",
    "Morning phone unlock delayed by 45 minutes on average (positive habit)."
  ],
  "recommendations": [
    "Set an app reminder on YouTube starting at 10:45 PM.",
    "Charge your phone across the room to reinforce your late-night wind-down routine."
  ],
  "generated_at": "2026-11-20T18:40:00Z"
}
```

*Fallback Response (When <3 days of recorded usage)* (`200 OK`):
```json
{
  "insight_id": null,
  "status": "INSUFFICIENT_DATA",
  "title": "More Usage Data Needed",
  "summary": "We require at least 3 days of recorded device activity before generating personalized weekly habit assessments. Keep your mobile companion connected to unlock insights.",
  "minimum_days_required": 3,
  "recorded_days": 1
}
```

---

## 7. Privacy & Data Lifecycle Endpoints

### 7.1 Export User Data
- **GET** `/data/export`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response** (`200 OK` - downloadable `application/json`):
```json
{
  "export_version": "1.0",
  "exported_at": "2026-11-20T18:45:00Z",
  "user_profile": { "email": "user@example.com", "timezone": "America/New_York" },
  "registered_devices": [...],
  "daily_summaries": [...],
  "goals_and_limits": [...],
  "ai_insights": [...]
}
```

### 7.2 Irrevocable Account Deletion
- **POST** `/data/delete-account`
- **Headers**: `Authorization: Bearer <TOKEN>`
- **Request Body**:
```json
{
  "confirm_password": "SecurePassword123!"
}
```
- **Response** (`200 OK`):
```json
{
  "status": "purged",
  "message": "User account and all associated telemetry, summaries, and device registrations have been permanently deleted."
}
```

---

## 8. Standardized Error Response Formats

All backend error payloads strictly adhere to standard HTTP status codes and JSON formatting:

### 8.1 Unauthorized (`401 Unauthorized`)
Returned when an access token is expired, missing, or has an invalid signature.
```json
{
  "error_code": "UNAUTHORIZED",
  "message": "Authentication token has expired or is invalid.",
  "timestamp": "2026-11-20T18:50:00Z"
}
```

### 8.2 Forbidden (`403 Forbidden`)
Returned when an authenticated user attempts to access a resource (device, export, goal) belonging to another user account.
```json
{
  "error_code": "FORBIDDEN",
  "message": "You do not have permission to access the requested resource.",
  "timestamp": "2026-11-20T18:50:00Z"
}
```

### 8.3 Validation Error (`422 Unprocessable Entity`)
Returned when request parameters or payload fail Pydantic schema validation.
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Input validation failed.",
  "details": [
    {
      "field": "body.timezone",
      "issue": "Invalid IANA timezone string."
    }
  ],
  "timestamp": "2026-11-20T18:50:00Z"
}
```
