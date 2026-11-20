# Tasks: Digital Wellbeing Platform

**Input**: Design documents from `/specs/001-digital-wellbeing-platform/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/api-contracts.md`, `quickstart.md`).
**Prerequisites**: Approved `spec.md`, `plan.md`, and project constitution.
**Architecture**: Modular Monolith Backend (FastAPI + PostgreSQL, Zero Redis), Lightweight Flutter Companion (Android & iOS), Next.js Web Dashboard, Google Gemini AI Insights.

---

## Format: `- [ ] [TaskID] [P?] [Story?] Description with exact file path`
- **[P]**: Can run in parallel (different files, no blocking dependencies).
- **[Story]**: Associated user story (e.g. `[US1]`, `[US2]`) for traceability.
- Every task includes **Dependencies**, **Expected Output**, and **Validation Criteria**.

---

## Phase 1: Setup (Shared Infrastructure & Environment)

**Purpose**: Initialize repository structure, package environments, and project configurations across backend, mobile, and web.

- [X] T001 Initialize backend modular monolith project structure and virtual environment in `backend/requirements.txt`
  - *Dependencies*: None
  - *Expected Output*: Clean Python 3.11+ environment with FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, and Pytest installed
  - *Validation*: `python -m pytest --version` executes successfully
- [X] T002 [P] Initialize Flutter mobile companion application workspace in `mobile/pubspec.yaml`
  - *Dependencies*: None
  - *Expected Output*: Flutter 3.22+ project configured with `drift`, `sqlite3`, `path_provider`, and `http`/`dio`, excluding heavy UI or ML packages
  - *Validation*: `flutter pub get` and `flutter test` execute with zero errors
- [X] T003 [P] Initialize Next.js web analytics dashboard in `frontend/package.json`
  - *Dependencies*: None
  - *Expected Output*: Next.js 14+ (App Router), React 18/19, TypeScript, Tailwind CSS, Lucide icons, and Recharts installed
  - *Validation*: `pnpm build` or `npm run build` succeeds
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
  - *Expected Output*: Migration script creating all 13 tables (`users`, `devices`, `app_usage_events`, `daily_usage_summaries`, etc.) with UUID PKs and indexes
  - *Validation*: `alembic upgrade head` creates all tables with constraints in PostgreSQL
- [X] T009 [P] Implement PostgreSQL-backed asynchronous task queue worker in `backend/app/core/task_queue.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Task enqueueing and worker consumer using `app_tasks` with `FOR UPDATE SKIP LOCKED` (replacing Redis)
  - *Validation*: Asynchronous test enqueues and processes a dummy background job
- [X] T010 [P] Implement base API router and global exception handlers in `backend/app/main.py`
  - *Dependencies*: T005, T006
  - *Expected Output*: FastAPI app instance mounting `/api/v1` routes with standardized JSON error formatting
  - *Validation*: `GET /docs` serves OpenAPI documentation
- [X] T011 [P] Implement Flutter embedded Drift/SQLite database and base DAOs in `mobile/lib/core/database/app_database.dart`
  - *Dependencies*: T002
  - *Expected Output*: Drift database class with tables for local events and sync queue
  - *Validation*: Drift schema migration and DAO unit tests pass in `flutter test`
- [X] T012 [P] Implement Flutter HTTP REST client with authentication interceptor in `mobile/lib/core/network/api_client.dart`
  - *Dependencies*: T002
  - *Expected Output*: Network client with automated JWT bearer attachment and retry logic
  - *Validation*: Mock HTTP client tests verify token injection and error handling
- [X] T013 [P] Implement Web dashboard layout, theme, and typed API fetch client in `frontend/src/lib/api.ts`
  - *Dependencies*: T003
  - *Expected Output*: Reusable REST client with auth token handling and base dashboard sidebar navigation
  - *Validation*: Frontend test renders navigation layout and handles mock fetch calls

---

## Phase 3: User Story 1 - Device Onboarding, Consent & Activity Tracking (Priority: P1) 🎯 MVP Part 1

**Goal**: Enable users to register an account, register their mobile device, record explicit tracking consent, and start tracking physical screen-unlocked time and foreground applications.

**Independent Test**: Onboard a fresh mobile client, authenticate with the backend, grant system permissions, use apps, and confirm raw events are recorded in local storage.

### Tests for User Story 1
- [ ] T014 [P] [US1] Integration tests for authentication and device registration endpoints in `backend/tests/integration/test_auth_device.py`
  - *Dependencies*: T006, T007, T008
  - *Expected Output*: Tests verifying `/auth/register`, `/auth/login`, and `/devices/register` with valid and invalid payloads
  - *Validation*: `pytest backend/tests/integration/test_auth_device.py` executes and asserts status codes
- [ ] T015 [P] [US1] Unit tests for Flutter permission state machine and onboarding controller in `mobile/test/features/onboarding_test.dart`
  - *Dependencies*: T011, T012
  - *Expected Output*: Unit tests asserting permission transition states and local consent storage
  - *Validation*: `flutter test mobile/test/features/onboarding_test.dart` passes

### Implementation for User Story 1
- [ ] T016 [P] [US1] Implement User and RefreshToken models in `backend/app/modules/auth/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: SQLAlchemy models mapped to `users` and `refresh_tokens` tables
  - *Validation*: Database queries create and retrieve user instances
- [ ] T017 [P] [US1] Implement Device and UserConsent models in `backend/app/modules/devices/models.py` and `backend/app/modules/consent/models.py`
  - *Dependencies*: T006, T008, T016
  - *Expected Output*: SQLAlchemy models mapped to `devices`, `device_capabilities`, and `user_consents`
  - *Validation*: Database queries persist device pairings and consent audit logs
- [ ] T018 [US1] Implement AuthService and auth router (`/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/me`) in `backend/app/modules/auth/router.py`
  - *Dependencies*: T007, T016
  - *Expected Output*: Registration, login, and authenticated user profile retrieval endpoints
  - *Validation*: T014 integration tests pass
- [ ] T019 [US1] Implement DeviceService and device router (`/api/v1/devices/register`, `/api/v1/devices`) in `backend/app/modules/devices/router.py`
  - *Dependencies*: T017, T018
  - *Expected Output*: Device registration and listing endpoints enforcing user isolation
  - *Validation*: T014 device integration tests pass
- [ ] T020 [P] [US1] Implement abstract Dart platform interface for device usage tracking in `mobile/lib/platform/device_usage_platform.dart`
  - *Dependencies*: T002
  - *Expected Output*: Abstract class `DeviceUsagePlatform` defining `checkPermissions()`, `requestPermissions()`, and `queryEvents()`
  - *Validation*: Mock platform implementation compiles cleanly
- [ ] T021 [US1] Implement Android native platform channel using `UsageStatsManager` and screen broadcast receivers in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/UsageStatsHandler.kt`
  - *Dependencies*: T020
  - *Expected Output*: Kotlin platform channel handling `ACTION_SCREEN_ON`/`OFF` and querying `UsageStatsManager.queryEvents()`
  - *Validation*: Android test runs on emulator and retrieves active foreground app
- [ ] T022 [US1] Implement iOS native platform channel using Apple Screen Time `FamilyControls` in `mobile/ios/Runner/ScreenTimeHandler.swift`
  - *Dependencies*: T020
  - *Expected Output*: Swift platform channel requesting `AuthorizationCenter.shared.requestAuthorization(for: .individual)`
  - *Validation*: iOS test confirms authorization callback handling
- [ ] T023 [US1] Implement Flutter onboarding screen with transparent consent prompt in `mobile/lib/features/onboarding/onboarding_screen.dart`
  - *Dependencies*: T012, T015, T020
  - *Expected Output*: UI screen presenting privacy commitments, account sign-in, and OS permission request button
  - *Validation*: T015 passes and UI renders in widget tests

---

## Phase 4: User Story 3 - Offline Caching & Resilient Synchronization (Priority: P2) 🎯 MVP Part 2

**Goal**: Buffer collected usage events locally on device and opportunistically synchronize with the backend with idempotent deduplication and retry handling.

**Independent Test**: Put mobile companion into airplane mode, generate usage, reconnect, trigger sync, and confirm records appear in backend PostgreSQL without duplicates.

### Tests for User Story 3
- [ ] T024 [P] [US3] Integration tests for `/api/v1/usage/sync` batch ingestion and idempotent duplicate rejection in `backend/tests/integration/test_usage_sync.py`
  - *Dependencies*: T006, T008, T019
  - *Expected Output*: Tests sending duplicate event UUID batches and verifying `duplicate_events_ignored` count
  - *Validation*: `pytest backend/tests/integration/test_usage_sync.py` passes
- [ ] T025 [P] [US3] Unit tests for Flutter offline storage DAO and SyncManager retry logic in `mobile/test/core/sync_manager_test.dart`
  - *Dependencies*: T011, T012
  - *Expected Output*: Tests verifying events remain in SQLite queue until HTTP 200 is received
  - *Validation*: `flutter test mobile/test/core/sync_manager_test.dart` passes

### Implementation for User Story 3
- [ ] T026 [P] [US3] Implement AppUsageEvent and ScreenActivityEvent SQLAlchemy models in `backend/app/modules/usage_ingestion/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models with `UNIQUE(device_id, event_uuid)` and timestamp indices
  - *Validation*: Models create records with unique UUID constraints in PostgreSQL
- [ ] T027 [US3] Implement UsageIngestionService with idempotent `ON CONFLICT DO NOTHING` logic in `backend/app/modules/usage_ingestion/service.py`
  - *Dependencies*: T026
  - *Expected Output*: Ingestion service inserting event batches and counting new vs. duplicate records
  - *Validation*: Service test confirms duplicate event UUIDs do not create duplicate rows
- [ ] T028 [US3] Implement usage synchronization endpoint (`POST /api/v1/usage/sync`) in `backend/app/modules/usage_ingestion/router.py`
  - *Dependencies*: T027
  - *Expected Output*: REST endpoint accepting sync batches and returning processed/duplicate counts
  - *Validation*: T024 integration tests pass
- [ ] T029 [US3] Implement Flutter local event storage and synchronization queue DAO in `mobile/lib/core/database/daos/usage_events_dao.dart`
  - *Dependencies*: T011
  - *Expected Output*: Drift DAO methods for batch insert, pending query, and acknowledged batch deletion
  - *Validation*: Local database CRUD tests pass
- [ ] T030 [US3] Implement Flutter SyncManager with periodic background sync via WorkManager/BGTaskScheduler in `mobile/lib/features/background/sync_manager.dart`
  - *Dependencies*: T012, T029
  - *Expected Output*: Sync orchestrator packaging pending events with client UUIDs, uploading, and purging acknowledged rows
  - *Validation*: T025 passes with mock HTTP server

---

## Phase 5: User Story 2 - Centralized Web Analytics & Usage History (Priority: P1) 🎯 MVP Part 3

**Goal**: Aggregate raw events into sessions and daily summaries; display screen time, app breakdowns, and historical trends on the Next.js web dashboard.

**Independent Test**: Ingest sample events for multiple dates, log into web dashboard, and verify accurate screen time totals, app breakdowns, and trend charts.

### Tests for User Story 2
- [ ] T031 [P] [US2] Unit tests for session derivation, sub-2s debouncing, and local timezone daily aggregation math in `backend/tests/unit/test_usage_processing.py`
  - *Dependencies*: T006
  - *Expected Output*: Unit tests asserting active screen-unlocked time calculation and sub-2s debounce merging
  - *Validation*: `pytest backend/tests/unit/test_usage_processing.py` passes
- [ ] T032 [P] [US2] Integration tests for analytics overview and historical reporting endpoints in `backend/tests/integration/test_analytics.py`
  - *Dependencies*: T006, T008, T028
  - *Expected Output*: Tests verifying `/api/v1/analytics/overview` and `/api/v1/analytics/history`
  - *Validation*: `pytest backend/tests/integration/test_analytics.py` passes
- [ ] T033 [P] [US2] Component tests for web dashboard overview charts in `frontend/src/tests/overview_chart.test.tsx`
  - *Dependencies*: T003, T013
  - *Expected Output*: React Testing Library tests asserting screen-time donut and top-apps bar chart rendering
  - *Validation*: `pnpm test` passes

### Implementation for User Story 2
- [ ] T034 [P] [US2] Implement DailyUsageSummary and AppDailySummary models in `backend/app/modules/usage_processing/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models mapped to `daily_usage_summaries` and `app_daily_summaries`
  - *Validation*: Database queries persist daily aggregated screen times and app allocations
- [ ] T035 [US2] Implement UsageProcessingService for session calculation, debouncing, and daily summarization in `backend/app/modules/usage_processing/service.py`
  - *Dependencies*: T026, T034
  - *Expected Output*: Aggregation service processing raw screen and app events into contiguous sessions and timezone-aware daily records
  - *Validation*: T031 passes
- [ ] T036 [US2] Implement AnalyticsService and endpoints (`/api/v1/analytics/overview`, `/api/v1/analytics/history`) in `backend/app/modules/analytics/router.py`
  - *Dependencies*: T034, T035
  - *Expected Output*: Analytics REST endpoints serving headline metrics, top apps, category percentages, and historical trends
  - *Validation*: T032 passes
- [ ] T037 [P] [US2] Implement Web dashboard overview page with headline metrics in `frontend/src/app/(dashboard)/page.tsx`
  - *Dependencies*: T013, T036
  - *Expected Output*: Responsive dashboard displaying daily screen time, total unlocks, session counts, and top-used apps
  - *Validation*: T033 component tests pass
- [ ] T038 [P] [US2] Implement Web dashboard historical trends and category distribution views in `frontend/src/app/(dashboard)/trends/page.tsx`
  - *Dependencies*: T013, T036
  - *Expected Output*: Interactive daily, weekly, and monthly trend line charts and category allocation pie charts
  - *Validation*: Manual verification at `http://localhost:3000/trends` renders mock data

---

## Phase 6: User Story 4 - Goal Setting & App Usage Guardrails (Priority: P2)

**Goal**: Allow users to set screen time and app duration limits; enforce limits via native iOS shielding or Android notifications/overlays, and track violations on the dashboard.

**Independent Test**: Set a 30-minute limit on an app, simulate usage, sync, and confirm breach alerts appear on the dashboard and mobile client.

### Tests for User Story 4
- [ ] T039 [P] [US4] Integration tests for goals and limits endpoints in `backend/tests/integration/test_goals_limits.py`
  - *Dependencies*: T006, T008, T018
  - *Expected Output*: Tests verifying `/api/v1/goals` and `/api/v1/limits` CRUD operations and violation logging
  - *Validation*: `pytest backend/tests/integration/test_goals_limits.py` passes
- [ ] T040 [P] [US4] Unit tests for Flutter app limit enforcement platform channel in `mobile/test/features/app_limiter_test.dart`
  - *Dependencies*: T011, T020
  - *Expected Output*: Unit tests asserting shield/notification trigger on threshold exceedance
  - *Validation*: `flutter test mobile/test/features/app_limiter_test.dart` passes

### Implementation for User Story 4
- [ ] T041 [P] [US4] Implement UsageGoal, AppLimit, and AppLimitViolation models in `backend/app/modules/goals_limits/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: Models mapped to `usage_goals`, `app_limits`, and `app_limit_violations`
  - *Validation*: Schema constraints enforce unique `(user_id, package_name)`
- [ ] T042 [US4] Implement Goals & Limits service and endpoints in `backend/app/modules/goals_limits/router.py`
  - *Dependencies*: T041
  - *Expected Output*: REST endpoints (`GET/POST /goals`, `GET/POST /limits`) and breach evaluation logic
  - *Validation*: T039 passes
- [ ] T043 [P] [US4] Implement abstract Dart platform interface for app limiting in `mobile/lib/platform/app_limiter_platform.dart`
  - *Dependencies*: T020
  - *Expected Output*: Abstract interface `AppLimiterPlatform` defining `applyAppLimit()` and `clearAppLimit()`
  - *Validation*: Dart code compiles
- [ ] T044 [US4] Implement iOS `ManagedSettings` application shield plugin in `mobile/ios/Runner/AppShieldHandler.swift`
  - *Dependencies*: T043
  - *Expected Output*: Swift implementation shielding restricted application tokens via `ManagedSettingsStore`
  - *Validation*: Shield handler executes in iOS test environment
- [ ] T045 [US4] Implement Android high-priority notification and reminder overlay in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/LimitReminderHandler.kt`
  - *Dependencies*: T043
  - *Expected Output*: Kotlin implementation triggering notification with warning overlay intent when limited app opens
  - *Validation*: Android test validates notification dispatch
- [ ] T046 [P] [US4] Implement Web dashboard goal tracking and limit management page in `frontend/src/app/(dashboard)/goals/page.tsx`
  - *Dependencies*: T013, T042
  - *Expected Output*: Interactive UI for creating goals, setting app limits, and viewing violation histories
  - *Validation*: Goal creation and progress meters render cleanly

---

## Phase 7: User Story 6 - Supported Network Usage Visibility (Priority: P3)

**Goal**: Track Wi-Fi and mobile data bytes transferred per application on Android; display an informational "Platform Restricted" banner for iOS on the web dashboard.

**Independent Test**: Ingest network records on an Android device, verify Wi-Fi and mobile data breakdown on the dashboard, and verify iOS device view displays explicit restriction banner.

### Tests for User Story 6
- [ ] T047 [P] [US6] Integration tests for network telemetry sync in `backend/tests/integration/test_network_usage.py`
  - *Dependencies*: T006, T008, T019
  - *Expected Output*: Tests verifying `/api/v1/network/sync` batch ingestion and deduplication
  - *Validation*: `pytest backend/tests/integration/test_network_usage.py` passes

### Implementation for User Story 6
- [ ] T048 [P] [US6] Implement NetworkUsageEvent model in `backend/app/modules/network_usage/models.py`
  - *Dependencies*: T006, T008
  - *Expected Output*: SQLAlchemy model mapped to `network_usage_events` with byte counters and indices
  - *Validation*: Database persistence verified
- [ ] T049 [US6] Implement NetworkUsageService and sync endpoint (`POST /api/v1/network/sync`) in `backend/app/modules/network_usage/router.py`
  - *Dependencies*: T048
  - *Expected Output*: REST endpoint accepting daily per-app Wi-Fi and cellular Tx/Rx bytes
  - *Validation*: T047 passes
- [ ] T050 [P] [US6] Implement Android `NetworkStatsManager` platform collector in `mobile/android/app/src/main/kotlin/com/digitalwellbeing/telemetry/NetworkStatsHandler.kt`
  - *Dependencies*: T020
  - *Expected Output*: Kotlin channel querying `NetworkStatsManager.queryDetailsForUid()` for Wi-Fi and mobile data
  - *Validation*: Android emulator test queries network statistics for test apps
- [ ] T051 [P] [US6] Implement Web dashboard network telemetry card with Android metrics and iOS notice in `frontend/src/components/charts/NetworkTelemetryCard.tsx`
  - *Dependencies*: T013, T036
  - *Expected Output*: React component rendering Wi-Fi vs. mobile data charts for Android and "Platform Restricted" banner for iOS
  - *Validation*: Storybook or component render test passes for both platform states

---

## Phase 8: User Story 5 - AI-Powered Habit Insights & Recommendations (Priority: P3)

**Goal**: Aggregate user weekly usage summaries, invoke Google Gemini API with privacy-vetted metrics, and present structured recommendations on the web dashboard.

**Independent Test**: Trigger insight generation for a user with simulated multi-day history and verify structured JSON advice is returned and rendered on the dashboard.

### Tests for User Story 5
- [ ] T052 [P] [US5] Unit and integration tests for Gemini prompt construction and Pydantic schema parsing in `backend/tests/integration/test_ai_insights.py`
  - *Dependencies*: T006, T008, T035
  - *Expected Output*: Mocked Gemini API tests validating structured insight generation and fallback handling
  - *Validation*: `pytest backend/tests/integration/test_ai_insights.py` passes

### Implementation for User Story 5
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
- [ ] T057 [P] [US5] Implement Web dashboard AI insights view with wellbeing score cards in `frontend/src/app/(dashboard)/insights/page.tsx`
  - *Dependencies*: T013, T056
  - *Expected Output*: Responsive UI displaying habit patterns, score badge, and actionable advice cards
  - *Validation*: Manual verification renders insight cards cleanly

---

## Phase 9: User Story 7 - Privacy Control, Data Export & Account Deletion (Priority: P1)

**Goal**: Provide self-service full-data JSON export and immediate ($<5\text{s}$) cascading account deletion.

**Independent Test**: Request data export and verify JSON download; submit account deletion and confirm zero rows remain in PostgreSQL.

### Tests for User Story 7
- [ ] T058 [P] [US7] Integration tests for JSON data export and cascading hard account deletion in `backend/tests/integration/test_data_management.py`
  - *Dependencies*: T006, T008, T018, T028
  - *Expected Output*: Tests validating complete JSON export payload and asserting 0 rows across all tables post-deletion
  - *Validation*: `pytest backend/tests/integration/test_data_management.py` passes

### Implementation for User Story 7
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
- [ ] T062 [P] [US7] Implement Web dashboard privacy & data management settings page in `frontend/src/app/(dashboard)/settings/page.tsx`
  - *Dependencies*: T013, T061
  - *Expected Output*: UI screen with "Export My Data" download button and "Delete Account" confirmation dialog
  - *Validation*: Export triggers file download; delete dialog requires password input
- [ ] T063 [P] [US7] Implement Flutter mobile consent revocation and local database wipe in `mobile/lib/features/onboarding/consent_service.dart`
  - *Dependencies*: T011, T012
  - *Expected Output*: Method clearing Drift SQLite tables and notifying server of consent revocation
  - *Validation*: Mobile unit test confirms local tables are wiped

---

## Phase 10: Polish, Optimization & Cross-Cutting Concerns

**Purpose**: Binary optimization, battery profiling, security verification, and end-to-end quickstart execution.

- [ ] T064 [P] Optimize Flutter mobile release configuration for package size ($<35\text{ MB}$) in `mobile/android/app/build.gradle` and `mobile/ios/Podfile`
  - *Dependencies*: T021, T022, T030
  - *Expected Output*: ProGuard/R8 rules, split per ABI, asset minimization, and tree shaking enabled
  - *Validation*: `flutter build apk --release` and `flutter build ipa --release` produce packages under 35 MB
- [ ] T065 [P] Implement automated battery consumption profiling harness in `mobile/test/benchmark/battery_test.dart`
  - *Dependencies*: T030
  - *Expected Output*: Test measuring CPU wake locks and background polling intervals
  - *Validation*: Confirms background execution adheres to $\le 3\%$ battery budget over 24 hours
- [ ] T066 [P] Execute security penetration and privacy compliance test suite in `backend/tests/security/test_security_audit.py`
  - *Dependencies*: T018, T028, T061
  - *Expected Output*: Automated test asserting zero communication content logging, strict TLS, and JWT expiration
  - *Validation*: `pytest backend/tests/security/test_security_audit.py` passes
- [ ] T067 [P] Create multi-container Docker Compose configuration in `docker-compose.yml`
  - *Dependencies*: T001, T003
  - *Expected Output*: Compose file orchestrating FastAPI backend, PostgreSQL 16, and Next.js web dashboard
  - *Validation*: `docker compose config` validates syntax
- [ ] T068 Execute end-to-end validation scenarios following `specs/001-digital-wellbeing-platform/quickstart.md`
  - *Dependencies*: T018, T028, T036, T056, T061, T067
  - *Expected Output*: Full run of Scenarios 1–6 proving registration, device pairing, telemetry sync, analytics, and AI insights work end-to-end
  - *Validation*: All 6 quickstart validation steps pass successfully

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Setup (Phase 1)**: Can start immediately across backend, mobile, and web.
2. **Foundational (Phase 2)**: Depends on Phase 1 completion. **Blocks all User Stories.**
3. **User Story 1 (Phase 3 - P1)**: Core onboarding & raw tracking. Prerequisite for synchronization.
4. **User Story 3 (Phase 4 - P2)**: Offline storage and idempotent batch sync. Prerequisite for server analytics.
5. **User Story 2 (Phase 5 - P1)**: Usage aggregation and web dashboard analytics. (Completes core MVP).
6. **User Story 4 (Phase 6 - P2)**: Goal setting & app limit enforcement.
7. **User Story 6 (Phase 7 - P3)**: Network telemetry tracking.
8. **User Story 5 (Phase 8 - P3)**: AI habit insights generation.
9. **User Story 7 (Phase 9 - P1)**: Privacy control, data export & account deletion.
10. **Polish & Validation (Phase 10)**: Final cross-cutting validation and optimization.

### Parallel Execution Strategy
- Tasks marked with `[P]` touch separate files and have no blockers within their phase.
- Backend, Flutter, and Web dashboard tracks can be developed in parallel by separate engineers once Phase 2 (Foundational) is complete:
  - **Backend Engineer**: Focuses on T014, T016–T019, T024, T026–T028, T031, T034–T036, T039, T041–T042, T047–T049, T052–T056, T058–T061.
  - **Mobile Engineer**: Focuses on T015, T020–T023, T025, T029–T030, T040, T043–T045, T050, T063, T064–T065.
  - **Web Engineer**: Focuses on T033, T037–T038, T046, T051, T057, T062.

---

## MVP Scope Recommendation

The recommended initial Minimum Viable Product (MVP) consists of:
- **Phase 1: Setup**
- **Phase 2: Foundational Infrastructure**
- **Phase 3: User Story 1 (Device Onboarding & Permission Granting)**
- **Phase 4: User Story 3 (Offline Ingestion & Idempotent Sync)**
- **Phase 5: User Story 2 (Aggregated Daily Screen Time & Web Dashboard Analytics)**

Completing Phases 1 through 5 delivers a fully functional, end-to-end working loop: a user registers, connects their phone, tracks physical screen time and app usage, synchronizes data, and views their digital wellbeing on the web dashboard.
