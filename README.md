# Digital Wellbeing Backend Platform

A privacy-first, modular monolith backend powering cross-platform digital wellbeing tracking, screen-time analytics, daily guardrails, and behavioral habit management.

Built with **Python 3.11+**, **FastAPI**, **PostgreSQL 16+ (async SQLAlchemy 2.0 & asyncpg)**, and **Alembic**.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Architectural Principles](#architectural-principles)
- [Core Features](#core-features)
- [System Architecture & Directory Structure](#system-architecture--directory-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Database Configuration & Migrations](#database-configuration--migrations)
- [Running the Application](#running-the-application)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Comprehensive API Reference & Testing Guide](#comprehensive-api-reference--testing-guide)
  - [1. Health & Diagnostics](#1-health--diagnostics)
  - [2. Identity & Authentication](#2-identity--authentication)
  - [3. Device Management](#3-device-management)
  - [4. Privacy & Consent Management (GDPR)](#4-privacy--consent-management-gdpr)
  - [5. Usage Telemetry Ingestion & Idempotent Sync](#5-usage-telemetry-ingestion--idempotent-sync)
  - [6. Centralized Analytics & History](#6-centralized-analytics--history)
  - [7. Goals & Application Limits Guardrails](#7-goals--application-limits-guardrails)
- [Background Task Queue (Zero Redis)](#background-task-queue-zero-redis)

---

## About the Project

The Digital Wellbeing Platform captures personal device usage telemetry (screen unlock/lock events, app foreground sessions, and notification counts) and processes it into meaningful daily aggregations, health trends, and usage guardrails.

This repository hosts the **Backend Modular Monolith API**, responsible for:
- User identity, token lifecycle, and session tracking.
- Client device pairing and synchronization state.
- Strictly gated GDPR data collection consent management.
- High-throughput, idempotent telemetry ingestion from client devices.
- Anti-flicker debouncing and active unlocked screen-time derivation.
- Analytics reporting (headline metrics, hourly distributions, category shares, and historical trends).
- Application usage limits and breach audit logging.

---

## Architectural Principles

1. **Modular Monolith**: Single deployable FastAPI service separated into clean, bounded domain modules (`auth`, `devices`, `consent`, `usage_ingestion`, `usage_processing`, `analytics`, `goals_limits`).
2. **PostgreSQL Only (Zero Redis)**:
   - All state, sessions, and asynchronous background tasks are managed directly in PostgreSQL.
   - Background tasks utilize an `app_tasks` table with atomic `FOR UPDATE SKIP LOCKED` row-level locking, eliminating the operational overhead and memory cost of external queue brokers.
3. **Privacy-by-Design & GDPR Compliance**:
   - Ingestion is rejected unless the user explicitly grants active consent.
   - Revoking consent prevents subsequent ingestion and triggers audit logging.
4. **Idempotent Synchronization**:
   - Client sync batches contain client-generated UUIDs (`event_uuid`).
   - The database enforces `UNIQUE(device_id, event_uuid)` with `ON CONFLICT DO NOTHING`, safely tolerating offline retries and flaky mobile networks without double-counting screen time.
5. **Anti-Flicker Debouncing & Active Unlocked Screen Time**:
   - Foreground app switches shorter than 2 seconds are consolidated to prevent sensor noise from corrupting analytics.
   - Only foreground app sessions that overlap with active screen-unlocked state count toward daily screen time.

---

## Core Features

- **Authentication & Security**: Argon2id password hashing, short-lived JWT access tokens (15m), and database-tracked rotating refresh tokens (30d).
- **Device Management**: Register and track multiple mobile/desktop client instances per user with last-heartbeat tracking.
- **Granular Consent**: Manage consent types (`DATA_COLLECTION`, `ANALYTICS`, `AI_COACHING`) with full audit history.
- **Batch Ingestion (`/api/v1/usage/sync`)**: High-throughput ingestion of `ScreenActivityEvent` (screen on/off/unlock) and `AppUsageEvent` (app foreground/background).
- **Session Derivation**: Automatically stitch raw events into contiguous sessions and compute local timezone daily summaries.
- **Aggregated Analytics**: Query headline statistics, top apps, category distribution percentages, and multi-day historical comparisons.
- **Goals & App Limits**: Configure total daily screen-time goals, category limits, per-app duration caps, and inspect violation breach logs.

---

## System Architecture & Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py                 # Central v1 router mounting all submodules
│   ├── core/
│   │   ├── config.py                     # Pydantic v2 application settings
│   │   ├── database.py                   # Async SQLAlchemy engine, session maker, Base
│   │   ├── dependencies.py               # JWT authentication and user resolution
│   │   ├── security.py                   # Password hashing (Argon2id) & JWT token utilities
│   │   └── task_queue.py                 # PostgreSQL-backed worker queue (FOR UPDATE SKIP LOCKED)
│   ├── modules/
│   │   ├── analytics/                    # Analytics REST endpoints & aggregation queries
│   │   ├── auth/                         # User registration, login, refresh tokens
│   │   ├── consent/                      # GDPR consent grant, revocation & audit logs
│   │   ├── devices/                      # Device registration & heartbeat tracking
│   │   ├── goals_limits/                 # Screen-time goals, app limits, violation logging
│   │   ├── usage_ingestion/              # Raw telemetry ingestion & idempotent sync
│   │   └── usage_processing/             # Debouncing, sessionization & daily summarization
│   └── main.py                           # FastAPI application entrypoint & middleware
├── migrations/                           # Alembic database migrations
├── specs/                                # SpecKit specification & engineering documentation
├── tests/
│   ├── integration/                      # API endpoint integration test suite
│   └── unit/                             # Mathematical & unit test suite
├── .env.example                          # Sample environment configuration
├── alembic.ini                           # Alembic migration configuration
├── pyproject.toml                        # Project metadata & build tool configuration
└── requirements.txt                      # Production & test dependencies
```

---

## Prerequisites

- **Python**: Version `3.11` or higher
- **PostgreSQL / Supabase**: PostgreSQL 16+ or a free cloud database on [Supabase](https://supabase.com)
- **uv** (strongly recommended, ultra-fast Python package & project manager) or standard **pip** / **venv**
- **Git**

> [!TIP]
> **Why `uv`?** `uv` installs packages in seconds, manages virtual environments automatically, and runs scripts/tests reproducibly without activating the virtualenv manually.
> To install `uv` (if not already installed):
> - **Windows (PowerShell)**: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
> - **macOS / Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## Installation & Setup

### 1. Clone & Navigate to Backend
```bash
git clone <repository-url>
cd backend
```

### 2. Environment Setup with `uv` (Recommended)

Create the virtual environment and install all dependencies in seconds:

```bash
# 1. Create virtual environment
uv venv

# 2. Install dependencies (including email-validator, asyncpg, fastapi, pytest, ruff)
uv pip install -r requirements.txt
```

*(Alternative: Standard `pip` & `venv`)*
<details>
<summary>Click here for traditional pip / venv instructions</summary>

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
</details>

---

## Supabase Database Configuration

The application is fully compatible with **Supabase PostgreSQL**. You can connect via either Direct Connection (Session mode) or Supabase Connection Pooler (Supavisor / Transaction mode).

### 1. Obtain Supabase Connection String
In your [Supabase Dashboard](https://supabase.com/dashboard):
1. Navigate to **Project Settings** -> **Database**.
2. Under **Connection string**, select **URI**:
   - **Direct Connection (Recommended, Session mode, Port 5432)**:
     ```text
     postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
     ```
   - **Connection Pooler (Transaction mode, Port 6543)**:
     ```text
     postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
     ```
   *(Note: Remember to prefix the URI with `postgresql+asyncpg://` for async SQLAlchemy support. The application automatically disables statement caches when connecting via port 6543 pooler).*

### 2. Configure `.env`
An active `.env` file is located at the project root. Populate it with your Supabase credentials:

```dotenv
# Database Connection (Supabase asyncpg URI)
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Supabase API Credentials (Project Settings -> API)
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_publishable_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_secret_key

# Security & JWT
JWT_SECRET_KEY=94e75bb876d5462cf10fba4c185fae44b059dbcd64b6e56ea7ff975bf810ec54
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# External AI Provider (Google Gemini)
GEMINI_API_KEY=

# Runtime Environment
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

---

## Database Migrations

Once your `DATABASE_URL` in `.env` points to your Supabase instance (or local PostgreSQL), apply the migrations to create all required tables, foreign keys, and indexes:

### Run Migrations with `uv`
```bash
uv run alembic upgrade head
```

*(Or if using standard virtualenv):*
```bash
alembic upgrade head
```

To roll back one migration:
```bash
uv run alembic downgrade -1
```

### Seed Administrative User
Seed or update an administrative user account in Supabase/PostgreSQL with Argon2id password hashing and full platform consents:

```bash
# Seed default admin (admin@digitalwellbeing.com / Admin@123456)
uv run python scripts/seed_admin.py

# Or seed custom credentials
uv run python scripts/seed_admin.py --email admin@example.com --password "MySecurePassword123!" --timezone "America/New_York"
```

The script will also output a pre-signed administrative JWT Bearer token ready for instant API calls to `/api/v1/admin/dashboard/overview`.

---

## Running the Application

### Start Development Server with `uv`
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will initialize on `http://localhost:8000`.

### Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## Testing & Quality Assurance

Run the automated test suite with `uv`:

```bash
# Run all unit and integration tests
uv run pytest tests/ -v

# Run unit tests only
uv run pytest tests/unit/ -v

# Run integration tests only
uv run pytest tests/integration/ -v

# Run tests with test coverage report
uv run pytest --cov=app tests/

# Run Ruff linter
uv run ruff check .
```

---

## Comprehensive API Reference & Testing Guide

All protected endpoints require the HTTP header:
`Authorization: Bearer <access_token>`

Standard error responses follow the format:
```json
{
  "error": {
    "code": "UNAUTHORIZED | VALIDATION_ERROR | CONFLICT | NOT_FOUND | FORBIDDEN",
    "message": "Human-readable explanation"
  }
}
```

---

### 1. Health & Diagnostics

#### `GET /health`
Verify server operational status.
```bash
curl -X GET http://localhost:8000/health
```
**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "digital-wellbeing-backend"
}
```

#### `GET /api/v1/health`
Verify API version 1 router health.
```bash
curl -X GET http://localhost:8000/api/v1/health
```
**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "v1"
}
```

---

### 2. Identity & Authentication

#### `POST /api/v1/auth/register`
Register a new user account. Passwords are automatically hashed using Argon2id.
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "display_name": "Alex Smith",
    "timezone": "America/New_York"
  }'
```
**Response (201 Created):**
```json
{
  "user_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "email": "user@example.com",
  "display_name": "Alex Smith",
  "timezone": "America/New_York",
  "created_at": "2026-11-21T06:00:00Z"
}
```

#### `POST /api/v1/auth/login`
Authenticate and obtain JWT access token and rotating refresh token.
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }'
```
**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "d748f328-1f6b-4e1b-b467-11ef85966df3",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### `POST /api/v1/auth/refresh`
Exchange a valid refresh token for a new access token and rotated refresh token.
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "d748f328-1f6b-4e1b-b467-11ef85966df3"
  }'
```
**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "a1990c74-2e91-49fa-8cc8-31be1d4a0f44",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### 3. Device Management

#### `POST /api/v1/devices/register`
Register or update client device metadata and record device heartbeat.
```bash
curl -X POST http://localhost:8000/api/v1/devices/register \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_identifier": "11111111-2222-3333-4444-555555555555",
    "platform": "android",
    "device_model": "Pixel 8 Pro",
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
**Response (201 Created):**
```json
{
  "device_id": "c1f8872b-819a-4c91-9e73-1256ff258167",
  "status": "registered",
  "registered_at": "2026-11-21T06:05:00Z"
}
```

---

### 4. Privacy & Consent Management (GDPR)

Telemetry ingestion is strictly blocked unless `DATA_COLLECTION` consent is actively granted.

#### `POST /api/v1/consent/grant`
Explicitly grant consent for a purpose (`DATA_COLLECTION`, `ANALYTICS`, or `AI_COACHING`).
```bash
curl -X POST http://localhost:8000/api/v1/consent/grant \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "consent_type": "DATA_COLLECTION",
    "policy_version": "1.0.0"
  }'
```
**Response (200 OK):**
```json
{
  "consent_type": "DATA_COLLECTION",
  "is_granted": true,
  "granted_at": "2026-11-21T06:06:00Z",
  "policy_version": "1.0.0"
}
```

#### `POST /api/v1/consent/revoke`
Revoke consent for a specific purpose.
```bash
curl -X POST http://localhost:8000/api/v1/consent/revoke \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "consent_type": "DATA_COLLECTION"
  }'
```
**Response (200 OK):**
```json
{
  "consent_type": "DATA_COLLECTION",
  "is_granted": false,
  "revoked_at": "2026-11-21T06:07:00Z"
}
```

#### `GET /api/v1/consent/status`
Retrieve user's active consent configuration.
```bash
curl -X GET http://localhost:8000/api/v1/consent/status \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "consents": [
    {
      "consent_type": "DATA_COLLECTION",
      "is_granted": true,
      "policy_version": "1.0.0",
      "updated_at": "2026-11-21T06:06:00Z"
    }
  ]
}
```

---

### 5. Usage Telemetry Ingestion & Idempotent Sync

#### `POST /api/v1/usage/sync`
Ingest raw batches of screen activity events and foreground app usage events.
Safe to retry: events matching existing `(device_id, event_uuid)` are skipped without error.
```bash
curl -X POST http://localhost:8000/api/v1/usage/sync \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "c1f8872b-819a-4c91-9e73-1256ff258167",
    "screen_events": [
      {
        "event_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "event_type": "SCREEN_UNLOCK",
        "timestamp": "2026-11-21T09:00:00Z"
      },
      {
        "event_uuid": "7ba85f64-5717-4562-b3fc-2c963f66afa7",
        "event_type": "SCREEN_OFF",
        "timestamp": "2026-11-21T09:45:00Z"
      }
    ],
    "app_events": [
      {
        "event_uuid": "a1a85f64-5717-4562-b3fc-2c963f66afa8",
        "package_name": "com.android.chrome",
        "app_title": "Google Chrome",
        "event_type": "FOREGROUND",
        "timestamp": "2026-11-21T09:02:00Z"
      },
      {
        "event_uuid": "b2a85f64-5717-4562-b3fc-2c963f66afa9",
        "package_name": "com.android.chrome",
        "app_title": "Google Chrome",
        "event_type": "BACKGROUND",
        "timestamp": "2026-11-21T09:30:00Z"
      }
    ]
  }'
```
**Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "screen_events_processed": 2,
  "screen_events_duplicates": 0,
  "app_events_processed": 2,
  "app_events_duplicates": 0
}
```

---

### 6. Centralized Analytics & History

#### `GET /api/v1/analytics/overview`
Get daily headline metrics, category allocation breakdown, and top-used applications for a target date (defaults to today).
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/overview?target_date=2026-11-21" \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "summary_date": "2026-11-21",
  "total_screen_time_seconds": 7200,
  "unlock_count": 28,
  "top_apps": [
    {
      "package_name": "com.android.chrome",
      "app_title": "Google Chrome",
      "category_name": "Productivity",
      "duration_seconds": 3600
    },
    {
      "package_name": "com.spotify.music",
      "app_title": "Spotify",
      "category_name": "Entertainment",
      "duration_seconds": 1800
    }
  ],
  "categories": [
    {
      "category_name": "Productivity",
      "duration_seconds": 3600,
      "percentage": 50.0
    },
    {
      "category_name": "Entertainment",
      "duration_seconds": 1800,
      "percentage": 25.0
    }
  ]
}
```

#### `GET /api/v1/analytics/history`
Query daily aggregated metrics across a specified date range.
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/history?start_date=2026-11-14&end_date=2026-11-21" \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "start_date": "2026-11-14",
  "end_date": "2026-11-21",
  "days": [
    {
      "date": "2026-11-21",
      "total_screen_time_seconds": 7200,
      "unlock_count": 28
    }
  ]
}
```

---

### 7. Goals & Application Limits Guardrails

#### `POST /api/v1/goals`
Configure daily total screen-time or category goals.
```bash
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_type": "TOTAL_SCREEN_TIME",
    "max_duration_seconds": 10800
  }'
```
**Response (201 Created):**
```json
{
  "goal_id": "84d7a8e2-0498-4c6e-8260-234b4198c644",
  "target_type": "TOTAL_SCREEN_TIME",
  "category_id": null,
  "max_duration_seconds": 10800,
  "is_active": true
}
```

#### `GET /api/v1/goals`
List all active usage goals configured by the user.
```bash
curl -X GET http://localhost:8000/api/v1/goals \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "goals": [
    {
      "goal_id": "84d7a8e2-0498-4c6e-8260-234b4198c644",
      "target_type": "TOTAL_SCREEN_TIME",
      "category_id": null,
      "max_duration_seconds": 10800,
      "is_active": true
    }
  ]
}
```

#### `POST /api/v1/limits`
Set or update daily duration limit for an application package.
```bash
curl -X POST http://localhost:8000/api/v1/limits \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "package_name": "com.instagram.android",
    "max_duration_seconds": 1800
  }'
```
**Response (201 Created):**
```json
{
  "limit_id": "673f8e52-1f48-4cb2-87ad-a6d8591cb342",
  "package_name": "com.instagram.android",
  "max_duration_seconds": 1800,
  "is_active": true
}
```

#### `GET /api/v1/limits`
List all active application limits configured by user.
```bash
curl -X GET http://localhost:8000/api/v1/limits \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "limits": [
    {
      "limit_id": "673f8e52-1f48-4cb2-87ad-a6d8591cb342",
      "package_name": "com.instagram.android",
      "max_duration_seconds": 1800,
      "is_active": true
    }
  ]
}
```

#### `GET /api/v1/limits/violations`
Retrieve historical log of limit breaches.
```bash
curl -X GET http://localhost:8000/api/v1/limits/violations \
  -H "Authorization: Bearer <access_token>"
```
**Response (200 OK):**
```json
{
  "violations": [
    {
      "id": "119f8e52-2f48-4cb2-87ad-a6d8591cb101",
      "package_name": "com.instagram.android",
      "violation_date": "2026-11-20",
      "actual_duration_seconds": 2100,
      "limit_duration_seconds": 1800,
      "created_at": "2026-11-20T21:45:00Z"
    }
  ]
}
```

---

## Background Task Queue (Zero Redis)

The application handles delayed and scheduled tasks (e.g. daily usage aggregation, limit breach checks) through PostgreSQL using [app/core/task_queue.py](file:///C:/Users/HARSH/Desktop/Digital%20Wellbeing/backend/app/core/task_queue.py).

### How It Works
- Tasks are inserted into the `app_tasks` table with a task name, JSON payload, and status (`PENDING`).
- Workers query pending jobs using `SELECT ... FOR UPDATE SKIP LOCKED` and update status to `PROCESSING`.
- Completed tasks transition to `COMPLETED` or `FAILED` (with automatic retry countdown and backoff).
- This delivers transactional reliability with database ACID guarantees while completely avoiding Redis or external broker dependencies.

---

## License

Proprietary and confidential. All rights reserved.
