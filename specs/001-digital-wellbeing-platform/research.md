# Research & Architectural Decisions: Digital Wellbeing Platform

**Feature**: `001-digital-wellbeing-platform` | **Date**: 2026-11-20

This document consolidates architectural evaluations, technical decisions, and validated best practices for the Digital Wellbeing platform implementation.

---

## 1. Backend Architecture: Modular Monolith

### Decision
Implement the backend as a single, unified modular monolith in Python using FastAPI, SQLAlchemy 2.0 (async), Alembic, and Pydantic v2.

### Domain Boundaries
The application is partitioned into clear, loosely-coupled domain modules under `app/modules/`:
1. `auth`: User registration, authentication, JWT issuing, password hashing, and token revocation.
2. `users`: Profile management, timezone preference, account settings.
3. `devices`: Physical device registration, capability profiling, push tokens, and heartbeat/sync metadata.
4. `consent`: Explicit user privacy consent tracking and versioned consent history.
5. `usage_ingestion`: Validation, deduplication, and persistence of client usage batches.
6. `usage_processing`: Contiguous session derivation, debouncing, and local calendar-day summary aggregations.
7. `network_usage`: Android per-app Wi-Fi and cellular traffic tracking; iOS platform restriction notices.
8. `analytics`: Daily, weekly, and monthly trend calculations, category allocations, and top app rankings.
9. `goals_limits`: Screen time target monitoring, app usage threshold evaluations, and breach logging.
10. `ai_insights`: Prompt construction, Gemini API invocation with aggregated summaries, and insight persistence.
11. `data_management`: Self-service full-data JSON export and cascading immediate hard deletion.

### Rationale
- Personal wellbeing tracking is user-scoped and does not require complex distributed event networks.
- A modular monolith allows clean transactional boundaries, shared database connection pooling, zero network hops between domains, and straightforward local/CI testing.

### Alternatives Considered & Rejected
- **Microservices**: Rejected by project constitution (Principle 1 & 15). Microservices would introduce network serialization overhead, distributed tracing requirements, and multi-service deployment complexity without organizational justification.
- **Django**: Provides an all-in-one framework, but FastAPI offers superior native async I/O performance, automatic OpenAPI documentation, and tighter Pydantic type validation for high-throughput mobile telemetry batches.

---

## 2. Infrastructure: Zero-Redis Background Processing & Storage

### Decision
PostgreSQL 16+ is the sole persistent datastore. Background processing and scheduled maintenance jobs are implemented without Redis or message brokers.

### Technical Implementation
1. **Lightweight Post-Response Tasks**: Use FastAPI's native `BackgroundTasks` for fire-and-forget operations that can complete in under 5 seconds (e.g., logging an audit event, triggering immediate batch aggregation recalculation).
2. **Persistent Background Tasks & Scheduled Aggregations**: Use an internal PostgreSQL-backed task queue pattern (`app_tasks` table with `FOR UPDATE SKIP LOCKED`) or lightweight scheduled coroutines (`asyncio` scheduler / `APScheduler` backed by PostgreSQL job locks).
3. **Caching**: Utilize in-memory LRU caching (`cachetools` / async memoization) for static/infrequent metadata (app categories, system capabilities) and rely on PostgreSQL compound indexes for time-series analytical queries.

### Rationale
- Principle 5 of the Constitution explicitly forbids Redis to avoid redundant operational infrastructure, separate memory tuning, and cache invalidation bugs.
- PostgreSQL easily handles concurrent batch ingestion and summary calculations for personal tracking workloads when indexed appropriately.

### Alternatives Considered & Rejected
- **Redis + Celery**: Rejected by Constitution. Adds operational overhead, requires a separate managed cluster or container, and introduces distributed state failure points.
- **RabbitMQ / Kafka**: Vast over-engineering for personal usage telemetry synchronization.

---

## 3. Mobile Client Architecture: Lightweight Flutter Companion

### Decision
Build a single Flutter/Dart mobile client supporting Android (8.0+) and iOS (16.0+) designed primarily as an unobtrusive, battery-friendly background data collector.

### Technical Guidelines
1. **Lightweight Footprint**: Exclude heavy graphing engines, animation suites, and machine learning runtimes. Analytical visualizations are reserved for the Next.js web dashboard.
2. **Local Storage Engine**: Use `drift` (with `sqlite3`) for type-safe, reactive, low-overhead local relational storage. Drift operates efficiently in background isolates and handles transactions reliably.
3. **Background Scheduling**:
   - Android: `WorkManager` (via `workmanager` plugin or custom platform channel) to schedule periodic background sync windows while respecting Doze mode.
   - iOS: `BGTaskScheduler` (`BGAppRefreshTask` / `BGProcessingTask`) coupled with Apple Screen Time framework lifecycle events.
4. **Platform Abstraction**: All native OS calls are isolated behind abstract Dart interfaces (`DeviceUsagePlatform`, `NetworkTelemetryPlatform`, `AppLimiterPlatform`). Concrete platform implementations use Flutter `MethodChannel` and `EventChannel`.

### Rationale
- Satisfies Constitution Principles 2, 8, 9, and 10.
- Keeps release APK/AAB and IPA binary size under 35 MB and runtime battery consumption under 3% over 24 hours.

### Alternatives Considered & Rejected
- **Separate Native Android (Kotlin) & iOS (Swift) Apps**: Rejected by Constitution Principle 2 (requires maintaining two divergent client repositories).
- **React Native**: Heavier JavaScript runtime overhead, larger baseline binary size, and less predictable background thread performance compared to ahead-of-time (AOT) compiled Flutter/Dart.

---

## 4. Platform-Specific Integration & Restrictions

### Android Data Collection Strategy
- **Usage Tracking**: `UsageStatsManager.queryEvents()` retrieves atomic foreground (`ACTIVITY_RESUMED`) and background (`ACTIVITY_PAUSED` / `ACTIVITY_STOPPED`) transitions.
- **Screen State**: Intent filters for `ACTION_SCREEN_ON`, `ACTION_SCREEN_OFF`, and `ACTION_USER_PRESENT` capture precise active unlocked screen time.
- **Network Stats**: `NetworkStatsManager.queryDetailsForUid()` retrieves transmitted (Tx) and received (Rx) bytes per UID for `TYPE_WIFI` and `TYPE_MOBILE`.
- **Permissions**: Guided intent to `Settings.ACTION_USAGE_ACCESS_SETTINGS` and runtime prompt for `POST_NOTIFICATIONS`.

### iOS Data Collection & Screen Time Strategy
- **Frameworks**: `FamilyControls`, `DeviceActivity`, and `ManagedSettings`.
- **Capabilities**:
  - `DeviceActivityReport` extension creates system-rendered privacy-safe views of screen time and app usage.
  - `ManagedSettings` applies native shields to restricted apps when user limits are reached.
  - Screen Time authorization requested via `AuthorizationCenter.shared.requestAuthorization(for: .individual)`.
- **Network Telemetry Constraint**: Public Apple APIs do **not** provide per-app network data to third-party apps. The client and backend explicitly denote this as "Platform Restricted" rather than failing or showing zero.

---

## 5. Session Calculation & Deduplication Architecture

### Session Calculation Rules
1. **Active Screen Time**: Calculated from consecutive `SCREEN_UNLOCKED` to `SCREEN_OFF` or `SCREEN_LOCKED` intervals.
2. **App Foreground Sessions**: Bounded strictly by `APP_RESUMED` and (`APP_PAUSED` OR `SCREEN_OFF` OR `SCREEN_LOCKED`).
3. **Debouncing**: Brief transitions under 2,000 milliseconds (e.g., pulling down the notification shade or quick app switching) are merged to preserve session continuity without artificial fragmentation.

### Idempotent Synchronization
1. **Client Event UUIDs**: Every raw event generated on the mobile device is assigned a UUIDv4 upon creation in the local SQLite/Drift database.
2. **Server Deduplication**: PostgreSQL enforces a `UNIQUE(device_id, event_uuid)` constraint. Ingestion uses:
   ```sql
   INSERT INTO app_usage_events (...) VALUES (...)
   ON CONFLICT (device_id, event_uuid) DO NOTHING;
   ```
3. **Batch Acknowledgment**: Server responds with `{ "status": "success", "processed_count": N, "duplicate_count": M }`. Client only clears or marks records as synchronized upon receiving HTTP 200/201.

---

## 6. Web Dashboard Architecture (Next.js, React, TypeScript)

### Decision
Develop the web analytics dashboard with Next.js 14+ (App Router), React, TypeScript, and Tailwind CSS.

### Key Architecture Components
- **Server/Client Components**: Server Components handle initial authentication checks and data fetching; Client Components handle interactive chart tooltips, date-range filtering, and goal configurations.
- **Visualizations**: Use a lightweight, accessible charting library (`recharts` or native SVG charts) to render:
  - Daily screen time donut & bar breakdown.
  - Weekly and monthly historical trend lines.
  - Category distribution breakdowns (Productivity, Social, Entertainment, etc.).
  - Goal progress meters and limit violation heatmaps.
  - Supported Android network usage (Wi-Fi vs. Mobile data) with iOS restriction banners.
- **API Client**: Strongly-typed fetch wrapper communicating exclusively with `/api/v1` backend REST endpoints.

---

## 7. AI Insights Integration (Google Gemini API)

### Decision
Integrate Google Gemini API (`gemini-1.5-flash` or `gemini-2.0-flash`) via the official Google GenAI Python SDK (`google-genai`).

### Privacy-Preserving Pipeline
1. **Aggregation First**: The backend Analytics service calculates daily and weekly summary statistics (total screen time, category percentages, top 5 used applications, hour-of-day peak usage distribution, goal completion rates).
2. **Anonymized Payload**: Telemetry payloads sent to Gemini contain zero user identifiers, email addresses, device serial numbers, or message contents.
3. **Structured Prompting**: Gemini is prompted to generate structured JSON conforming to a Pydantic schema:
   - `summary`: High-level assessment of the week's digital balance.
   - `key_patterns`: Detected habits (e.g., late-night usage spikes, heavy morning social media).
   - `actionable_recommendations`: 2-3 specific, achievable behavioral adjustments.
   - `wellbeing_score`: Normalized index (1-100) based on goal compliance and balanced distribution.
4. **LangGraph Evaluation**: Standard structured prompting with Pydantic output parsing satisfies all requirements. LangGraph is kept optional and will only be introduced if multi-step autonomous agent loops (e.g., interactive multi-turn coaching) are ratified.

---

## 8. Security, Privacy & Data Lifecycle

### Security Controls
- **Authentication**: JWT access tokens (15-minute expiration) + secure rotating refresh tokens (30-day expiration, stored in HTTP-only, secure, SameSite cookies).
- **Password Security**: Argon2id or bcrypt with high work factor.
- **Transport**: Strict HTTPS/TLS 1.3 across all communication.
- **Authorization**: Strict tenant/user isolation: every database query filters on `user_id` derived from the validated JWT token.

### Privacy & Data Deletion
- **No Content Inspection**: Explicit architectural guarantee: no message text, notification content, keystrokes, or screen captures are ever queried or stored.
- **Consent Audit**: Every consent grant or revocation is recorded with timestamp and version in `user_consents`.
- **Data Export**: Endpoint `/api/v1/data/export` generates a comprehensive JSON export of all user activity.
- **Hard Deletion**: Endpoint `/api/v1/data/delete-account` triggers an immediate cascading database deletion (`ON DELETE CASCADE`) purging all user profile data, devices, raw telemetry, summaries, goals, and AI insights within 5 seconds.
