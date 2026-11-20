# Implementation Plan: Digital Wellbeing Platform

**Branch**: `001-digital-wellbeing-platform` | **Date**: 2026-11-20 | **Spec**: [specs/001-digital-wellbeing-platform/spec.md](spec.md)

**Input**: Feature specification from `specs/001-digital-wellbeing-platform/spec.md` and ratified engineering constitution in `.specify/memory/constitution.md`.

---

## Summary

The Digital Wellbeing platform provides personal digital activity tracking across Android and iOS devices, centralized in a responsive Next.js web dashboard. The architecture follows a strict **modular monolith** backend built with Python FastAPI and PostgreSQL (with zero Redis/microservice overhead). The mobile client is a single lightweight Flutter application focused exclusively on unobtrusive local data collection, offline caching, and opportunistic background synchronization. Analytics, historical trend aggregations, and Gemini-powered AI habit recommendations reside on the server and are visualized on the web.

---

## Technical Context

- **Backend Language/Version**: Python 3.11+
- **Backend Framework**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), Alembic
- **Mobile Language/Version**: Flutter 3.22+, Dart 3.4+
- **Mobile Framework/Storage**: Flutter platform channels, `drift` / `sqlite3` (embedded local database)
- **Web Language/Version**: TypeScript 5.x, React 18/19, Next.js 14+ (App Router), Tailwind CSS
- **Primary Database**: PostgreSQL 16+ (UUID primary keys, UTC storage, composite deduplication indices)
- **Infrastructure / Caching**: No Redis; database-backed job queue (`app_tasks` with `FOR UPDATE SKIP LOCKED`) and FastAPI `BackgroundTasks`
- **AI Integration**: Google Gemini API (`gemini-1.5-flash` / `gemini-2.0-flash`) via `google-genai` SDK
- **Testing**: `pytest` + `pytest-asyncio` + `httpx` (backend); `flutter_test` (mobile); `vitest` + React Testing Library (web)
- **Security & Privacy**: JWT (access/rotating refresh tokens), Argon2id/bcrypt, TLS 1.3, granular consent audit trail, cascading immediate hard deletion

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Compliance Status | Justification / Design Reference |
|---|---|:---:|---|
| **1. Modular Monolith** | Backend as one deployable application; clear module boundaries | **PASS** | Organized into 11 distinct domain modules under `app/modules/`. |
| **2. Cross-Platform Flutter** | Single Flutter codebase for Android and iOS | **PASS** | Shared Flutter codebase in `mobile/`; no separate native app forks. |
| **3. FastAPI Backend** | Python FastAPI with RESTful `/api/v1` routes | **PASS** | Asynchronous FastAPI endpoints with Pydantic request/response schemas. |
| **4. PostgreSQL Primary DB** | Sole primary relational datastore with strict constraints | **PASS** | PostgreSQL 16+ with UUIDs, UTC timestamps, and deduplication indices. |
| **5. Zero-Redis Infrastructure** | No Redis or external brokers; database-backed jobs | **PASS** | Zero Redis dependencies; background processing uses `app_tasks` in PostgreSQL. |
| **6. Next.js Web Dashboard** | Next.js, React, TypeScript for rich analytics | **PASS** | Next.js App Router in `frontend/` consuming REST `/api/v1` endpoints. |
| **7. Gemini AI Insights** | Gemini API on aggregated privacy-vetted summaries | **PASS** | AI receives pre-aggregated daily summaries only; no raw telemetry or PII. |
| **8. Lightweight Mobile App** | Minimal mobile footprint; no heavy charts or local ML | **PASS** | Local SQLite storage via Drift; binary target $<35\text{ MB}$; battery $\le 3\%$. |
| **9. Platform Abstraction** | Native APIs isolated behind Flutter platform interfaces | **PASS** | Abstract Dart interfaces (`DeviceUsagePlatform`, `NetworkTelemetryPlatform`). |
| **10. Platform Compliance** | Respect Android permissions & Apple Screen Time limits | **PASS** | `UsageStatsManager` on Android; `FamilyControls`/`ManagedSettings` on iOS; network telemetry explicitly denoted as restricted on iOS. |
| **11. Privacy & Deletion** | Secure auth, explicit consent, instant hard deletion | **PASS** | JWT + Argon2id; `user_consents` audit table; hard delete in $<5\text{s}$. |
| **12. Clean Architecture** | Inward dependencies, standardized naming | **PASS** | Clean layering (Presentation, Domain, Infrastructure); PEP 8 & Effective Dart. |
| **13. Rigorous Testing** | Unit tests for business logic; integration tests for APIs | **PASS** | Pytest async integration suite; Flutter isolate tests; Web component tests. |
| **14. Spec-First Development** | Approved specification & plan before code | **PASS** | Formal Spec Kit flow followed (`spec.md` -> `plan.md` -> `tasks.md`). |
| **15. Simplicity / YAGNI** | No unnecessary services or complexity | **PASS** | Direct SQL queries, standard HTTP REST, and native framework capabilities. |

*Gate Evaluation*: **All 15 constitutional gates passed.** Zero violations.

---

## Project Structure & Source Code Layout

The project repository is structured into distinct, clean sub-projects:

```text
Digital Wellbeing/
├── backend/                             # Python FastAPI Modular Monolith
│   ├── app/
│   │   ├── core/                        # Global configuration, database session, security
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── modules/                     # Domain modules (encapsulated)
│   │   │   ├── auth/                    # Registration, JWT, login, tokens
│   │   │   ├── users/                   # Profile, timezone settings
│   │   │   ├── devices/                 # Device registration, capabilities
│   │   │   ├── consent/                 # Audit logging of consent
│   │   │   ├── usage_ingestion/         # Batch ingestion, deduplication
│   │   │   ├── usage_processing/        # Session calculation, daily summarization
│   │   │   ├── network_usage/           # Android network telemetry & iOS notices
│   │   │   ├── analytics/               # Overview, historical trends, top apps
│   │   │   ├── goals_limits/            # Screen time goals, app limits, breach logs
│   │   │   ├── ai_insights/             # Gemini prompt pipeline & insight storage
│   │   │   └── data_management/         # JSON data export, account hard deletion
│   │   └── main.py                      # FastAPI application entrypoint
│   ├── alembic/                         # Database schema migrations
│   ├── tests/                           # Unit and integration test suite
│   │   ├── unit/
│   │   └── integration/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                            # Next.js 14+ Web Analytics Dashboard
│   ├── src/
│   │   ├── app/                         # App Router pages and layouts
│   │   │   ├── (auth)/login/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── page.tsx             # Overview dashboard
│   │   │   │   ├── apps/page.tsx        # App-wise analytics
│   │   │   │   ├── trends/page.tsx      # Daily/Weekly/Monthly reports
│   │   │   │   ├── goals/page.tsx       # Goals & App Limits
│   │   │   │   ├── insights/page.tsx    # Gemini AI recommendations
│   │   │   │   └── settings/page.tsx    # Account, consent, export, delete
│   │   │   └── layout.tsx
│   │   ├── components/                  # UI components (charts, cards, nav)
│   │   │   ├── charts/
│   │   │   ├── layout/
│   │   │   └── ui/
│   │   ├── lib/                         # API client, auth helpers, formatting
│   │   └── types/                       # Shared TypeScript interfaces
│   ├── package.json
│   └── tailwind.config.ts
│
├── mobile/                              # Flutter Cross-Platform Companion
│   ├── lib/
│   │   ├── core/                        # Network client, local database, constants
│   │   │   ├── database/                # Drift / SQLite schema & DAOs
│   │   │   └── network/                 # Retrofit / Dio API sync client
│   │   ├── platform/                    # Abstract platform interfaces
│   │   │   ├── device_usage_platform.dart
│   │   │   ├── network_telemetry_platform.dart
│   │   │   └── app_limiter_platform.dart
│   │   ├── features/                    # Lightweight UI & state
│   │   │   ├── onboarding/              # Permission walkthrough & consent
│   │   │   ├── status/                  # Sync status, last upload, health
│   │   │   └── background/              # WorkManager & sync orchestrator
│   │   └── main.dart
│   ├── android/                         # Native Android platform channels (Kotlin)
│   ├── ios/                             # Native iOS Screen Time channels (Swift)
│   └── pubspec.yaml
│
└── specs/                               # Spec Kit Artifacts
    └── 001-digital-wellbeing-platform/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        └── contracts/
            └── api-contracts.md
```

---

## Detailed Architectural Plan (15 Core Dimensions)

### 1. System Architecture
The platform operates as a closed-loop data pipeline:
1. **Collector Tier**: Lightweight Flutter companion captures OS lifecycle events, buffers them locally in SQLite/Drift, and opportunistically syncs over HTTPS.
2. **Ingestion & Processing Tier**: FastAPI async endpoints validate JWT credentials, deduplicate events by client UUID, and store raw events in PostgreSQL. An internal processor aggregates raw intervals into contiguous usage sessions and calculates local calendar-day summaries according to user IANA timezones.
3. **Analytics Tier**: PostgreSQL compound indexes serve fast aggregated reports to the Next.js web dashboard.
4. **Intelligence Tier**: Google Gemini processes pre-aggregated weekly metrics and outputs structured behavioral recommendations.

### 2. Repository and Folder Structure
Organized as a unified multi-project repository:
- `backend/`: FastAPI application, Alembic migrations, database models, schemas, and Pytest suites.
- `frontend/`: Next.js App Router, Tailwind design system, Recharts data visualization.
- `mobile/`: Flutter client with clean platform abstraction isolating Android Kotlin and iOS Swift channels.

### 3. Backend Module Design
Adheres strictly to the modular monolith pattern:
- Each module in `app/modules/<name>/` owns its Pydantic schemas, SQLAlchemy models, service layer, and router.
- Inter-module communication uses direct Python service calls (no HTTP network hops or RPC).
- Transactional integrity is maintained through SQLAlchemy async sessions.

### 4. Flutter Module Design
The mobile app contains:
- `DatabaseModule`: Drift/SQLite managing tables `local_app_events`, `local_screen_events`, `local_network_events`, and `sync_queue`.
- `PlatformIntegrationModule`: Communicates via `MethodChannel('com.digitalwellbeing/telemetry')` to query native OS events.
- `SyncManager`: Periodically inspects `sync_queue`, packages batches with a new `sync_batch_id`, transmits to `/api/v1/usage/sync`, and deletes locally acknowledged records.
- `UIModule`: Simple, clean status screen displaying tracking status, permission state, and last sync timestamp.

### 5. Web Application Module Design
Next.js 14+ with App Router:
- `Overview`: Total screen time donut chart, unlock count, session count, top 5 applications.
- `App Analytics`: Deep-dive into specific applications, historical comparisons, category allocation.
- `Trends & Reports`: Day-over-day, week-over-week, and monthly usage shifts.
- `Goals & Limits`: Visual goal meters and warning badges for exceeded thresholds.
- `AI Insights`: Rendered cards with wellbeing scores, detected habit patterns, and actionable recommendations.
- `Settings`: Timezone configuration, device unlinking, raw data JSON export, and account deletion.

### 6. Database Schema and Relationships
Fully detailed in [data-model.md](data-model.md):
- 13 core relational tables with foreign key cascades on `user_id` and `device_id`.
- Composite uniqueness on `(device_id, event_uuid)` guaranteeing idempotent ingestion.
- Timestamps stored in UTC with explicit timezone columns for local calendar boundary aggregations.

### 7. API Contracts and Examples
Fully detailed in [contracts/api-contracts.md](contracts/api-contracts.md):
- Structured under `/api/v1`.
- Typed Pydantic request and response bodies.
- Explicit status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`).

### 8. Authentication and Authorization
- **Registration & Login**: Email/password authentication producing a short-lived JWT access token (15 minutes) and a rotating refresh token (30 days).
- **Passwords**: Hashed using Argon2id with unique salt.
- **Data Isolation**: All queries enforce `WHERE user_id = :current_user_id` extracted from verified JWT tokens. Cross-user access is impossible.

### 9. Data Synchronization and Offline Handling
- **Offline First**: All events are immediately written to local SQLite storage on the mobile device.
- **Opportunistic Sync**: Triggered upon network connection recovery or periodic WorkManager/BGTask execution.
- **Idempotency**: Retransmitted batches with duplicate event UUIDs are skipped via `ON CONFLICT DO NOTHING`, returning HTTP 200 so the client clears its queue.

### 10. Android and iOS Integration Strategy
- **Android**: Custom platform channel calling Kotlin `UsageStatsManager` (for app events) and broadcast receivers for `ACTION_SCREEN_ON`/`OFF`. `WorkManager` handles periodic background sync.
- **iOS**: Swift plugin invoking `FamilyControls` and `DeviceActivity`. Where entitlements exist, `ManagedSettings` applies native shields. Per-app network telemetry is marked as platform-restricted.
- **Isolation**: Shared Dart code only interacts with abstract interfaces, allowing full unit testing with mock platform handlers.

### 11. Network Tracking Feasibility and Limitations
- **Android**: `NetworkStatsManager` queries Wi-Fi and mobile data bytes per UID per calendar date. Supported and collected.
- **iOS**: Apple public APIs strictly prohibit third-party per-app network traffic inspection. iOS displays an explicit, transparent "Platform Restricted" notice on the dashboard.

### 12. AI Integration Architecture
- Pre-aggregated daily summaries and category percentages are formatted into structured prompts for the Google Gemini API.
- Zero raw personal messages, notification bodies, or user identifiers are ever transmitted to Gemini.
- Responses are validated against Pydantic schemas and persisted in `user_insights`.

### 13. Testing Strategy
- **Backend**: Pytest with asynchronous database fixtures testing registration, idempotent ingestion, daily aggregation math, and data deletion cascades.
- **Mobile**: Flutter unit and widget tests with mock platform channels verifying offline queuing and sync state transitions.
- **Web**: React Testing Library and Vitest testing dashboard chart rendering, timezone handling, and goal alerts.

### 14. Security and Privacy Requirements
- Zero personal communication tracking (no SMS, notifications, or keystrokes).
- Explicit, auditable user consent logged in `user_consents`.
- HTTPS/TLS 1.3 enforced for all transport.
- Self-service JSON data export.
- Immediate cascading hard deletion within 5 seconds.

### 15. Deployment Strategy
- **Containerization**: Standard Dockerfile for the FastAPI backend and Next.js frontend.
- **Reverse Proxy**: Nginx handling SSL termination and routing `/api/v1` to FastAPI and `/` to Next.js.
- **Target Hosting**: AWS (ECS Fargate or EC2) paired with AWS RDS PostgreSQL for reliable managed storage.

---

## Complexity Tracking

*No constitutional violations or unjustified complexity introduced. Redis and microservices excluded.*
