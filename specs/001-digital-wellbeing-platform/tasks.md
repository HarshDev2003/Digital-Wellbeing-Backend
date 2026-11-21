# Tasks: Digital Wellbeing Platform (Backend-Only Implementation Track)

**Input**: Design documents from `/specs/001-digital-wellbeing-platform/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/api-contracts.md`, `quickstart.md`).
**Prerequisites**: Approved `spec.md`, `plan.md`, and project constitution.
**Architecture**: Modular Monolith Backend (FastAPI + PostgreSQL, Zero Redis), Gemini AI Insights, database-backed task queue, and complete RESTful `/api/v1` contracts.

> [!IMPORTANT]
> **Active Implementation Scope: BACKEND ONLY**
> In accordance with project steering decisions, current active implementation is strictly scoped to the **Backend Modular Monolith** (Python, FastAPI, PostgreSQL, SQLAlchemy 2.0 async, Alembic, PostgreSQL task worker, Gemini AI service, and backend integration test suites).
> All **Flutter mobile companion** tasks and **Next.js web dashboard** tasks are architecturally specified and contracted herein, but **deferred from the current implementation cycle** and will be implemented separately in dedicated client tracks.

---

## Format: `- [ ] [TaskID] [P?] [Story?] Description with exact file path`
- **[P]**: Can run in parallel (different files, no blocking dependencies).
- **[Story]**: Associated user story (e.g. `[US1]`, `[US2]`) for traceability.
- Every task includes **Dependencies**, **Expected Output**, and **Validation Criteria**.

---

## Phase 1: Setup (Shared Infrastructure & Environment)

**Purpose**: Initialize repository structure, package environments, and project configurations.

- [X] T001 Initialize backend modular monolith project structure and virtual environment in `backend/requirements.txt`
  - *Dependencies*: None
  - *Expected Output*: Clean Python 3.11+ environment with FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, and Pytest installed
  - *Validation*: `python -m pytest --version` executes successfully
- [X] T002 [P] Initialize Flutter mobile companion application workspace scaffolding in `mobile/pubspec.yaml`
  - *Dependencies*: None
  - *Expected Output*: Workspace configuration for mobile companion client (implementation deferred to separate mobile track)
  - *Validation*: `flutter pub get` and `flutter test` execute with zero errors
- [X] T003 [P] Initialize Next.js web analytics dashboard workspace scaffolding in `frontend/package.json`
  - *Dependencies*: None
  - *Expected Output*: Workspace configuration for web analytics dashboard (implementation deferred to separate web track)
  - *Validation*: Workspace manifests created cleanly
- [X] T004 [P] Configure unified linting, formatting, and pre-commit checks in `.pre-commit-config.yaml`
  - *Dependencies*: None
  - *Expected Output*: Automated linters (`ruff` for Python, `flutter analyze` for Dart, `eslint`/`prettier` for TypeScript)
  - *Validation*: All lint commands run cleanly across the workspace

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core application infrastructure that MUST be complete before ANY user story can be implemented.

- [X] T005 [P] Implement core backend settings and environment configuration in `backend/app/core/config.py`
  - *Dependencies*: T001
  - *Expected Output*: Pydantic `Settings` class loading `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`, and CORS origins
  - *Validation*: Unit test loading settings with sample `.env` file passes
- [X] T006 [P] Implement asynchronous SQLAlchemy database engine and session dependency in `backend/app/core/database.py`
  - *Dependencies*: T001, T005
  - *Expected Output*: `AsyncEngine`, `async_sessionmaker`, and `get_db` FastAPI dependency
  - *Validation*: Script connecting to PostgreSQL test instance succeeds
- [X] T007 [P] Implement cryptographic security utilities (Argon2id hashing, JWT encode/decode) in `backend/app/core/security.py`
  - *Dependencies*: T001, T005
  - *Expected Output*: `hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, and JWT validator
  - *Validation*: Unit tests verify password hashing roundtrip and token expiration
- [X] T008 [P] Configure Alembic migrations and create initial database schema migration in `backend/alembic/versions/001_initial_schema.py`
  - *Dependencies*: T006, `data-model.md`
  - *Expected Output*: Migration script creating all 17 tables (`users`, `devices`, `app_usage_events`, `daily_usage_summaries`, etc.) with UUID PKs and indexes
  - *Validation*: `alembic upgrade head` creates all tables with constraints in PostgreSQL
- [X] T009 [P] Implement PostgreSQL-backed asynchronous task queue worker in `backend/app/core/task_queue.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Task enqueueing and worker consumer using `app_tasks` with `FOR UPDATE SKIP LOCKED` (replacing Redis)
  - *Validation*: Asynchronous test enqueues and processes a dummy background job
- [X] T010 [P] Implement base API router and global exception handlers in `backend/app/main.py`
  - *Dependencies*: T005, T006
  - *Expected Output*: FastAPI app instance mounting `/api/v1` routes with standardized JSON error formatting
  - *Validation*: `GET /docs` serves OpenAPI documentation
- [X] T011 [P] [DEFERRED: Mobile Track] Initial Drift SQLite schema shim in `mobile/lib/core/database/app_database.dart` (Full mobile companion implemented separately)
- [X] T012 [P] [DEFERRED: Mobile Track] Initial Flutter REST client shim in `mobile/lib/core/network/api_client.dart` (Full mobile companion implemented separately)
- [X] T013 [P] [DEFERRED: Web Track] Initial Web typed API client and layout shim in `frontend/src/lib/api.ts` (Full web dashboard implemented separately)

---

## Phase 3: User Story 1 - Device Onboarding, Consent & Activity Tracking (Priority: P1) 🎯 MVP Part 1

**Goal**: Enable users to register an account, register their mobile device, record explicit tracking consent, and provide backend persistence for physical screen-unlocked time and foreground applications.

**Independent Test**: Execute backend integration test registering user, recording consent, registering device, and querying device list.

### Tests for User Story 1
- [X] T014 [P] [US1] Integration tests for authentication and device registration endpoints in `backend/tests/integration/test_auth_device.py`
  - *Dependencies*: T006, T007, T008
  - *Expected Output*: Tests verifying `/auth/register`, `/auth/login`, and `/devices/register` with valid and invalid payloads
  - *Validation*: `pytest backend/tests/integration/test_auth_device.py` executes and asserts status codes
- [X] T015 [P] [US1] [DEFERRED: Mobile Track] Flutter onboarding controller tests in `mobile/test/features/onboarding_test.dart` (Full mobile companion implemented separately)

### Implementation for User Story 1
- [X] T016 [P] [US1] Implement User and RefreshToken models in `backend/app/modules/auth/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: SQLAlchemy models mapped to `users` and `refresh_tokens` tables
  - *Validation*: Database queries create and retrieve user instances
- [X] T017 [P] [US1] Implement Device and UserConsent models in `backend/app/modules/devices/models.py` and `backend/app/modules/consent/models.py`
  - *Dependencies*: T006, T008, T016
  - *Expected Output*: SQLAlchemy models mapped to `devices`, `device_capabilities`, and `user_consents`
  - *Validation*: Database queries persist device pairings and consent audit logs
- [X] T018 [US1] Implement AuthService and auth router (`/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`) in `backend/app/modules/auth/router.py`
  - *Dependencies*: T007, T016
  - *Expected Output*: Registration, login, and authenticated user profile retrieval endpoints
  - *Validation*: T014 integration tests pass
- [X] T019 [US1] Implement DeviceService and device router (`/api/v1/devices/register`, `/api/v1/devices`) in `backend/app/modules/devices/router.py`
  - *Dependencies*: T017, T018
  - *Expected Output*: Device registration and listing endpoints enforcing user isolation
  - *Validation*: T014 device integration tests pass
- [X] T020 [P] [US1] [DEFERRED: Mobile Track] Abstract Dart platform interface shim in `mobile/lib/platform/device_usage_platform.dart`
- [X] T021 [US1] [DEFERRED: Mobile Track] Android native channel shim in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/UsageStatsHandler.kt`
- [X] T022 [US1] [DEFERRED: Mobile Track] iOS native channel shim in `mobile/ios/Runner/ScreenTimeHandler.swift`
- [X] T023 [US1] [DEFERRED: Mobile Track] Flutter onboarding UI screen in `mobile/lib/features/onboarding/onboarding_screen.dart`

---

## Phase 4: User Story 3 - Offline Caching & Resilient Synchronization (Priority: P2) 🎯 MVP Part 2

**Goal**: Implement backend telemetry ingestion with idempotent deduplication and retry handling, supporting batch uploads from client devices.

**Independent Test**: Transmit duplicate event UUID batches to `/api/v1/usage/sync` and confirm database prevents duplicates while returning success.

### Tests for User Story 3
- [X] T024 [P] [US3] Integration tests for `/api/v1/usage/sync` batch ingestion and idempotent duplicate rejection in `backend/tests/integration/test_usage_sync.py`
  - *Dependencies*: T006, T008, T019
  - *Expected Output*: Tests sending duplicate event UUID batches and verifying `duplicate_events_ignored` count
  - *Validation*: `pytest backend/tests/integration/test_usage_sync.py` passes
- [-] T025 [P] [US3] [DEFERRED: Mobile Track - Implemented Separately] Unit tests for Flutter offline storage DAO and SyncManager retry logic in `mobile/test/core/sync_manager_test.dart`

### Implementation for User Story 3 (Backend)
- [X] T026 [P] [US3] Implement AppUsageEvent and ScreenActivityEvent SQLAlchemy models in `backend/app/modules/usage_ingestion/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models with `UNIQUE(device_id, event_uuid)` and timestamp indices
  - *Validation*: Models create records with unique UUID constraints in PostgreSQL
- [X] T027 [US3] Implement UsageIngestionService with idempotent `ON CONFLICT DO NOTHING` logic in `backend/app/modules/usage_ingestion/service.py`
  - *Dependencies*: T026
  - *Expected Output*: Ingestion service inserting event batches and counting new vs. duplicate records
  - *Validation*: Service test confirms duplicate event UUIDs do not create duplicate rows
- [X] T028 [US3] Implement usage synchronization endpoint (`POST /api/v1/usage/sync`) in `backend/app/modules/usage_ingestion/router.py`
  - *Dependencies*: T027
  - *Expected Output*: REST endpoint accepting sync batches and returning processed/duplicate counts
  - *Validation*: T024 integration tests pass
- [-] T029 [US3] [DEFERRED: Mobile Track - Implemented Separately] Implement Flutter local event storage and synchronization queue DAO in `mobile/lib/core/database/daos/usage_events_dao.dart`
- [-] T030 [US3] [DEFERRED: Mobile Track - Implemented Separately] Implement Flutter SyncManager with periodic background sync via WorkManager/BGTaskScheduler in `mobile/lib/features/background/sync_manager.dart`

---

## Phase 5: User Story 2 - Centralized Usage History & Daily Aggregation (Priority: P1) 🎯 MVP Part 3

**Goal**: Aggregate raw events into sessions and daily summaries; calculate active screen unlocked time, debounced application foreground intervals, and serve analytics REST APIs.

**Independent Test**: Ingest raw usage events, execute processing service, and confirm `/api/v1/analytics/overview` and `/api/v1/analytics/history` return accurate timezone-aware metrics.

### Tests for User Story 2
- [X] T031 [P] [US2] Unit tests for session derivation, sub-2s debouncing, and local timezone daily aggregation math in `backend/tests/unit/test_usage_processing.py`
  - *Dependencies*: T006
  - *Expected Output*: Unit tests asserting active screen-unlocked time calculation and sub-2s debounce merging
  - *Validation*: `pytest backend/tests/unit/test_usage_processing.py` passes
- [X] T032 [P] [US2] Integration tests for analytics overview and historical reporting endpoints in `backend/tests/integration/test_analytics.py`
  - *Dependencies*: T006, T008, T028
  - *Expected Output*: Tests verifying `/api/v1/analytics/overview` and `/api/v1/analytics/history`
  - *Validation*: `pytest backend/tests/integration/test_analytics.py` passes
- [-] T033 [P] [US2] [DEFERRED: Web Track - Implemented Separately] Component tests for web dashboard overview charts in `frontend/src/tests/overview_chart.test.tsx`

### Implementation for User Story 2 (Backend)
- [X] T034 [P] [US2] Implement DailyUsageSummary and AppDailySummary models in `backend/app/modules/usage_processing/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models mapped to `daily_usage_summaries` and `app_daily_summaries`
  - *Validation*: Database queries persist daily aggregated screen times and app allocations
- [X] T035 [US2] Implement UsageProcessingService for session calculation, debouncing, and daily summarization in `backend/app/modules/usage_processing/service.py`
  - *Dependencies*: T026, T034
  - *Expected Output*: Aggregation service processing raw screen and app events into contiguous sessions and timezone-aware daily records
  - *Validation*: T031 passes
- [X] T036 [US2] Implement AnalyticsService and endpoints (`/api/v1/analytics/overview`, `/api/v1/analytics/history`) in `backend/app/modules/analytics/router.py`
  - *Dependencies*: T034, T035
  - *Expected Output*: Analytics REST endpoints serving headline metrics, top apps, category percentages, and historical trends
  - *Validation*: T032 passes
- [-] T037 [P] [US2] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard overview page with headline metrics in `frontend/src/app/(dashboard)/page.tsx`
- [-] T038 [P] [US2] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard historical trends and category distribution views in `frontend/src/app/(dashboard)/trends/page.tsx`

---

## Phase 6: User Story 4 - Goal Setting & App Usage Guardrails (Priority: P2)

**Goal**: Allow users to set screen time and app duration limits; evaluate limit breaches on the backend and record historical violations.

**Independent Test**: Configure a 30-minute limit on an application, process 35 minutes of usage, and verify violation record is persisted and reported via `/api/v1/limits`.

### Tests for User Story 4
- [X] T039 [P] [US4] Integration tests for goals and limits endpoints in `backend/tests/integration/test_goals_limits.py`
  - *Dependencies*: T006, T008, T018
  - *Expected Output*: Tests verifying `/api/v1/goals` and `/api/v1/limits` CRUD operations and violation logging
  - *Validation*: `pytest backend/tests/integration/test_goals_limits.py` passes
- [-] T040 [P] [US4] [DEFERRED: Mobile Track - Implemented Separately] Unit tests for Flutter app limit enforcement platform channel in `mobile/test/features/app_limiter_test.dart`

### Implementation for User Story 4 (Backend)
- [X] T041 [P] [US4] Implement UsageGoal, AppLimit, and AppLimitViolation models in `backend/app/modules/goals_limits/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models mapped to `usage_goals`, `app_limits`, and `app_limit_violations`
  - *Validation*: Schema constraints enforce unique `(user_id, package_name)`
- [X] T042 [US4] Implement Goals & Limits service and endpoints in `backend/app/modules/goals_limits/router.py`
  - *Dependencies*: T041
  - *Expected Output*: REST endpoints (`GET/POST /goals`, `GET/POST /limits`) and breach evaluation logic
  - *Validation*: T039 passes
- [-] T043 [P] [US4] [DEFERRED: Mobile Track - Implemented Separately] Implement abstract Dart platform interface for app limiting in `mobile/lib/platform/app_limiter_platform.dart`
- [-] T044 [US4] [DEFERRED: Mobile Track - Implemented Separately] Implement iOS `ManagedSettings` application shield plugin in `mobile/ios/Runner/AppShieldHandler.swift`
- [-] T045 [US4] [DEFERRED: Mobile Track - Implemented Separately] Implement Android high-priority notification and reminder overlay in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/LimitReminderHandler.kt`
- [-] T046 [P] [US4] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard goal tracking and limit management page in `frontend/src/app/(dashboard)/goals/page.tsx`

---

## Phase 7: User Story 6 - Supported Network Usage Ingestion & Rest-State APIs (Priority: P3)

**Goal**: Ingest daily per-app Wi-Fi and mobile data transfer statistics; provide platform capability awareness (Android supported, iOS restricted).

**Independent Test**: Post network telemetry payload to `/api/v1/network/sync` and verify records are stored and correctly reflected in analytics endpoint.

### Tests for User Story 6
- [ ] T047 [P] [US6] Integration tests for network telemetry sync in `backend/tests/integration/test_network_usage.py`
  - *Dependencies*: T006, T008, T019
  - *Expected Output*: Tests verifying `/api/v1/network/sync` batch ingestion and deduplication
  - *Validation*: `pytest backend/tests/integration/test_network_usage.py` passes

### Implementation for User Story 6 (Backend)
- [ ] T048 [P] [US6] Implement NetworkUsageEvent model in `backend/app/modules/network_usage/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: SQLAlchemy model mapped to `network_usage_events` with byte counters and indices
  - *Validation*: Database persistence verified
- [ ] T049 [US6] Implement NetworkUsageService and sync endpoint (`POST /api/v1/network/sync`) in `backend/app/modules/network_usage/router.py`
  - *Dependencies*: T048
  - *Expected Output*: REST endpoint accepting daily per-app Wi-Fi and cellular Tx/Rx bytes
  - *Validation*: T047 passes
- [-] T050 [P] [US6] [DEFERRED: Mobile Track - Implemented Separately] Implement Android `NetworkStatsManager` platform collector in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/NetworkStatsHandler.kt`
- [-] T051 [P] [US6] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard network telemetry card with Android metrics and iOS notice in `frontend/src/components/charts/NetworkTelemetryCard.tsx`

---

## Phase 8: User Story 5 - AI-Powered Habit Insights & Recommendations (Priority: P3)

**Goal**: Aggregate weekly usage summaries, invoke Google Gemini API with privacy-vetted metrics, and serve structured habit advice.

**Independent Test**: Trigger insight generation for a user with simulated multi-day history and verify structured JSON advice is returned and saved in `user_insights`.

### Tests for User Story 5
- [ ] T052 [P] [US5] Unit and integration tests for Gemini prompt construction and Pydantic schema parsing in `backend/tests/integration/test_ai_insights.py`
  - *Dependencies*: T006, T008, T035
  - *Expected Output*: Mocked Gemini API tests validating structured insight generation and fallback handling
  - *Validation*: `pytest backend/tests/integration/test_ai_insights.py` passes

### Implementation for User Story 5 (Backend)
- [ ] T053 [P] [US5] Implement UserInsight model in `backend/app/modules/ai_insights/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: SQLAlchemy model mapped to `user_insights` table with JSONB structured data
  - *Validation*: Database queries persist insight records
- [ ] T054 [US5] Implement Google Gemini API client wrapper with structured output parsing in `backend/app/modules/ai_insights/gemini_client.py`
  - *Dependencies*: T005
  - *Expected Output*: Async client using `google-genai` SDK with Pydantic response validation and timeout handling
  - *Validation*: Mocked client test verifies prompt creation and schema validation
- [ ] T055 [US5] Implement AIInsightsService aggregating weekly summaries and generating insights in `backend/app/modules/ai_insights/service.py`
  - *Dependencies*: T035, T053, T054
  - *Expected Output*: Service fetching anonymized weekly aggregates, calling Gemini, and storing results
  - *Validation*: T052 passes
- [ ] T056 [US5] Implement AI insights endpoints (`POST /api/v1/ai/insights/generate`, `GET /api/v1/ai/insights`) in `backend/app/modules/ai_insights/router.py`
  - *Dependencies*: T055
  - *Expected Output*: REST endpoints to trigger and retrieve user insights
  - *Validation*: Integration tests assert insight retrieval
- [-] T057 [P] [US5] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard AI insights view with wellbeing score cards in `frontend/src/app/(dashboard)/insights/page.tsx`

---

## Phase 9: User Story 7 - Privacy Control, Data Export & Account Deletion (Priority: P1)

**Goal**: Provide self-service full-data JSON export and immediate ($<5\text{s}$) cascading account deletion.

**Independent Test**: Request data export and verify JSON payload; submit account deletion and confirm zero rows remain in PostgreSQL across all tables.

### Tests for User Story 7
- [ ] T058 [P] [US7] Integration tests for JSON data export and cascading hard account deletion in `backend/tests/integration/test_data_management.py`
  - *Dependencies*: T006, T008, T018, T028
  - *Expected Output*: Tests validating complete JSON export payload and asserting 0 rows across all tables post-deletion
  - *Validation*: `pytest backend/tests/integration/test_data_management.py` passes

### Implementation for User Story 7 (Backend)
- [ ] T059 [US7] Implement DataExportService compiling complete user activity history in `backend/app/modules/data_management/export_service.py`
  - *Dependencies*: T006, T016, T017, T026, T034
  - *Expected Output*: Service querying and packaging all user-owned records into structured JSON
  - *Validation*: Export test generates valid JSON structure
- [ ] T060 [US7] Implement AccountDeletionService executing cascading hard purge in `backend/app/modules/data_management/deletion_service.py`
  - *Dependencies*: T006, T016
  - *Expected Output*: Service verifying password and executing `DELETE FROM users WHERE id = :user_id`
  - *Validation*: T058 passes, verifying $<5\text{s}$ execution time
- [ ] T061 [US7] Implement data management endpoints (`GET /api/v1/data/export`, `POST /api/v1/data/delete-account`) in `backend/app/modules/data_management/router.py`
  - *Dependencies*: T059, T060
  - *Expected Output*: REST endpoints for streaming export JSON and confirming account deletion
  - *Validation*: T058 passes
- [-] T062 [P] [US7] [DEFERRED: Web Track - Implemented Separately] Implement Web dashboard privacy & data management settings page in `frontend/src/app/(dashboard)/settings/page.tsx`
- [-] T063 [P] [US7] [DEFERRED: Mobile Track - Implemented Separately] Implement Flutter mobile consent revocation and local database wipe in `mobile/lib/features/onboarding/consent_service.dart`

---

## Phase 10: Polish, Optimization & Backend Hardening

**Purpose**: Security verification, backend containerization, and API verification.

- [-] T064 [P] [DEFERRED: Mobile Track - Implemented Separately] Optimize Flutter mobile release configuration for package size ($<35\text{ MB}$) in `mobile/android/app/build.gradle` and `mobile/ios/Podfile`
- [-] T065 [P] [DEFERRED: Mobile Track - Implemented Separately] Implement automated battery consumption profiling harness in `mobile/test/benchmark/battery_test.dart`
- [ ] T066 [P] Execute security penetration and privacy compliance test suite in `backend/tests/security/test_security_audit.py`
  - *Dependencies*: T018, T028, T061
  - *Expected Output*: Automated test asserting zero communication content logging, strict TLS, and JWT expiration
  - *Validation*: `pytest backend/tests/security/test_security_audit.py` passes
- [ ] T067 [P] Create Docker Compose configuration for backend service and PostgreSQL in `docker-compose.yml`
  - *Dependencies*: T001
  - *Expected Output*: Compose file orchestrating FastAPI backend and PostgreSQL 16
  - *Validation*: `docker compose config` validates syntax
- [ ] T068 Execute end-to-end backend validation scenarios following `specs/001-digital-wellbeing-platform/quickstart.md`
  - *Dependencies*: T018, T028, T036, T056, T061, T067
  - *Expected Output*: Full run of Scenarios 1–6 proving registration, device pairing, telemetry sync, analytics, and AI insights work end-to-end via REST APIs
  - *Validation*: All 6 quickstart validation steps pass successfully

---

## Dependencies & Execution Order (Backend-Only Implementation)

### Active Execution Track (Backend Only)
1. **Foundational Backend (Phase 2)**: Core configuration, DB engine, security, Alembic migrations, PostgreSQL Task Queue worker, base API router. *(Completed)*
2. **User Story 1 (Phase 3 - US1)**: User registration, JWT login/refresh, consent audit logging, and device registration endpoints. *(Completed)*
3. **User Story 3 (Phase 4 - US3)**: Usage event models (`app_usage_events`, `screen_activity_events`), `UsageIngestionService` with idempotent deduplication, and `POST /api/v1/usage/sync` endpoint.
4. **User Story 2 (Phase 5 - US2)**: Daily summary models, `UsageProcessingService` with session derivation and 2s debouncing, and `/api/v1/analytics/overview` & `/api/v1/analytics/history` endpoints.
5. **User Story 4 (Phase 6 - US4)**: Goals, limits, and violation models, `GoalsLimitsService`, and `/api/v1/goals` & `/api/v1/limits` endpoints.
6. **User Story 6 (Phase 7 - US6)**: Network telemetry model, `NetworkUsageService`, and `POST /api/v1/network/sync` endpoint.
7. **User Story 5 (Phase 8 - US5)**: `UserInsight` model, `gemini_client.py` wrapper, `AIInsightsService`, and `/api/v1/ai/insights` endpoints.
8. **User Story 7 (Phase 9 - US7)**: `DataExportService`, `AccountDeletionService` with $<5\text{s}$ cascading purge, and `/api/v1/data/*` endpoints.
9. **Hardening & Verification (Phase 10)**: Security compliance test suite, Docker Compose for backend, and end-to-end API scenario verification.

### Client Implementation Tracks (Deferred / Implemented Separately)
- **Mobile Track (Flutter Companion)**: T025, T029, T030, T040, T043–T045, T050, T063–T065.
- **Web Track (Next.js Dashboard)**: T033, T037, T038, T046, T051, T057, T062.
