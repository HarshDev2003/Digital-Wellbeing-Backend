# Quickstart & Verification Guide: Digital Wellbeing Platform (Backend Monolith)

**Feature**: `001-digital-wellbeing-platform` | **Date**: 2026-11-20

This guide provides step-by-step instructions to set up the development environment, run the database migrations, launch the FastAPI modular monolith, simulate client telemetry synchronization, and verify the backend API endpoints.

> [!IMPORTANT]
> **Active Implementation Scope: Backend Only**
> This quickstart guide is focused on the **Backend Modular Monolith** (Python FastAPI, PostgreSQL, and Gemini AI integration). Mobile companion and Web frontend client applications are implemented separately in their own dedicated tracks.

---

## 1. Prerequisites

- **Python**: 3.11 or newer
- **PostgreSQL**: 15 or 16 running locally (or via Docker)
- **Gemini API Key**: Valid Google AI Studio API key (set in environment as `GEMINI_API_KEY`)
- *(Note: Node.js and Flutter are used in separate client implementation tracks)*

---

## 2. Environment Configuration

### Backend Environment (`backend/.env`)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/digital_wellbeing
JWT_SECRET_KEY=super-secret-jwt-key-for-development-only-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### Web Frontend Environment (`frontend/.env.local`)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 3. Database Initialization & Backend Setup

```bash
# 1. Start PostgreSQL container (if not running natively)
docker run --name digital-wellbeing-postgres \
  -e POSTGRES_DB=digital_wellbeing \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgres:16-alpine

# 2. Navigate to backend directory
cd backend

# 3. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Unix:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run database migrations
alembic upgrade head

# 6. Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

Verify backend health at `http://localhost:8000/docs` (Swagger UI).

---

## 4. End-to-End Validation Flow

### Scenario 1: User Registration & Login
```bash
# Register a test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@wellbeing.local",
    "password": "Password123!",
    "timezone": "America/New_York"
  }'

# Store the returned access_token for subsequent requests
```

### Scenario 2: Register a Mobile Device
```bash
curl -X POST http://localhost:8000/api/v1/devices/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "device_identifier": "dev-uuid-001",
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
  }'
```

### Scenario 3: Ingest Simulated Usage Telemetry Batch
```bash
curl -X POST http://localhost:8000/api/v1/usage/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "device_id": "<DEVICE_ID>",
    "sync_batch_id": "batch-101",
    "screen_events": [
      {
        "event_uuid": "e001-screen-on",
        "event_type": "SCREEN_ON",
        "timestamp": "2026-11-20T10:00:00Z"
      },
      {
        "event_uuid": "e002-unlocked",
        "event_type": "USER_UNLOCKED",
        "timestamp": "2026-11-20T10:00:02Z"
      },
      {
        "event_uuid": "e003-screen-off",
        "event_type": "SCREEN_OFF",
        "timestamp": "2026-11-20T11:30:00Z"
      }
    ],
    "app_events": [
      {
        "event_uuid": "e004-youtube",
        "package_name": "com.google.android.youtube",
        "start_time": "2026-11-20T10:05:00Z",
        "end_time": "2026-11-20T11:00:00Z",
        "duration_seconds": 3300
      }
    ]
  }'
```

### Scenario 4: Verify Idempotent Deduplication
Re-issue the exact same payload from Scenario 3.
**Expected Result**: HTTP 200 returned with `"duplicate_events_ignored": 4`, without doubling screen time or creating extra rows.

### Scenario 5: Query Analytics Overview
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/overview?date=2026-11-20" \
  -H "Authorization: Bearer <TOKEN>"
```
**Expected Result**:
- `total_screen_time_seconds`: 5398 (active screen unlocked duration: 10:00:02 to 11:30:00).
- `top_apps`: YouTube with 3300 seconds (55 minutes).

### Scenario 6: Trigger Gemini AI Insights
```bash
curl -X POST http://localhost:8000/api/v1/ai/insights/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "timeframe": "WEEKLY",
    "start_date": "2026-11-14",
    "end_date": "2026-11-20"
  }'
```
**Expected Result**: Structured JSON response with narrative advice, habit score, and recommendations.

---

## 5. Web Dashboard Setup

```bash
cd ../frontend
pnpm install
pnpm dev
```
Open `http://localhost:3000` to view the web dashboard with responsive charts, goal progress bars, and AI insight cards.

---

## 6. Automated Test Suite Execution

```bash
# Backend Unit & Integration Tests (PostgreSQL)
cd backend
pytest -v --cov=app tests/

# Mobile Tests
cd ../mobile
flutter test

# Frontend Unit Tests
cd ../frontend
pnpm test
```
