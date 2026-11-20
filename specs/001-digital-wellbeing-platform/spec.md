# Feature Specification: Digital Wellbeing Platform

**Feature Branch**: `001-digital-wellbeing-platform`

**Created**: 2026-11-20

**Status**: Draft

**Input**: User description: "Create the initial product specification for Digital Wellbeing. Read: docs/PRD.md, docs/TECH_SPEC.md, The project constitution. Product requirements: Build a personal digital wellbeing platform that helps users understand and manage their mobile activity. The system must include: 1. A Flutter mobile application for Android and iOS. 2. Mobile data collection with appropriate platform permissions. 3. Screen-time tracking. 4. Application-wise usage tracking. 5. Network usage tracking where supported. 6. Offline storage and background synchronization. 7. A FastAPI backend. 8. A PostgreSQL database. 9. A Next.js web dashboard. 10. Daily, weekly and monthly usage analytics. 11. Usage goals and supported application limits. 12. Gemini-powered AI insights."

---

## Clarifications

### Session 2026-11-20
- Q: What metric determines the total daily screen time displayed on the dashboard? → A: Active Screen-Unlocked Duration (Total time the physical screen is turned on and unlocked; individual app foreground times are sub-breakdowns within this window).
- Q: How should an application foreground session boundary be calculated when the screen locks or quick app switches occur? → A: Screen-Lock Bound & Debounced (Session starts on app foreground and terminates immediately when the app enters the background OR screen locks/turns off; micro-interruptions under 2 seconds are smoothed).
- Q: How should application limit enforcement behave across Android and iOS when a user exceeds their daily threshold? → A: Platform-Maximal Enforcement (Native shielding/lockout on iOS via ManagedSettings where permitted; high-priority notifications and reminder overlays on Android; full violation analytics on the web dashboard).
- Q: How should duplicate usage events be handled when retransmitted during background synchronization? → A: Client-Assigned UUIDs with Idempotent Ingestion (Client generates a UUID for each usage event; backend detects duplicates by UUID, skips re-insertion, and returns success to clear client queues).
- Q: Which network usage metrics should be tracked on Android, and how should network tracking be represented on iOS? → A: Per-App Wi-Fi & Cellular on Android; Explicit Restriction on iOS (Android tracks daily uploaded/downloaded bytes partitioned by Wi-Fi and mobile data per app; iOS displays an informational "Platform Restricted" banner with zero false data).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Device Onboarding, Consent & Activity Tracking (Priority: P1)

As an individual smartphone user, I want to install a lightweight mobile companion application on my Android or iOS device, review transparent permission requests, and grant explicit consent so that my daily screen time and application usage are tracked accurately and automatically in the background.

**Why this priority**: Without reliable, permitted on-device data collection, no downstream analytics, goal tracking, or wellbeing insights are possible. This is the foundational prerequisite for the entire product.

**Independent Test**: Can be verified by onboarding a fresh mobile installation, granting the requested system permissions, using several device applications over a test period, and confirming that raw foreground intervals and screen durations are correctly captured in local storage.

**Acceptance Scenarios**:

1. **Given** a user opens the mobile companion app for the first time, **When** they complete account sign-in, **Then** they are presented with an onboarding screen explaining what data is collected, how it is used, and a clear prompt to grant device usage permissions.
2. **Given** an Android device, **When** the user proceeds to grant permissions, **Then** the application guides the user to the native Usage Access system settings screen and updates its status once permission is verified.
3. **Given** an iOS device, **When** the user proceeds to grant permissions, **Then** the application triggers the system Screen Time authorization prompt and updates its status once authorized.
4. **Given** valid permissions are granted, **When** the user interacts with various applications throughout the day, **Then** the mobile companion records foreground application transitions and screen-on durations in local storage without requiring manual user intervention.

---

### User Story 2 - Centralized Web Analytics & Usage History (Priority: P1)

As a health-conscious user, I want to access a responsive web dashboard from my desktop or tablet browser to inspect my total daily screen time, application-wise usage breakdowns, category allocations, and historical trends across daily, weekly, and monthly views.

**Why this priority**: The web dashboard is the central analytical interface of the platform. It provides the actionable visibility that allows users to understand and reflect upon their digital habits.

**Independent Test**: Can be verified by logging into the web dashboard with an account having synchronized usage history and verifying that daily screen time totals, application breakdowns, top-used apps, and date-range filters render consistent summaries matching actual device usage.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the web dashboard, **When** they navigate to the overview page, **Then** they see their total daily screen time, total app sessions, and a ranked list of top-used applications for the current day in their local timezone.
2. **Given** synchronized multi-day usage history, **When** the user switches between daily, weekly, and monthly views, **Then** the dashboard displays historical usage charts, day-over-day trends, and category distribution percentages.
3. **Given** multiple registered devices under a single user account, **When** the user views the dashboard, **Then** they can view combined activity or filter statistics by a specific registered device.

---

### User Story 3 - Offline Caching & Resilient Synchronization (Priority: P2)

As a mobile user with variable connectivity (e.g., during transit or in low-coverage zones), I want my device activity to be cached safely on my device and opportunistically synchronized with the server when a network connection is available, without losing data or creating duplicate records.

**Why this priority**: Mobile devices frequently lose internet connectivity. Reliable offline caching guarantees continuous habit tracking without data loss or skewing analytics.

**Independent Test**: Can be verified by running the mobile companion in airplane mode for 4 hours while opening multiple apps, reconnecting to the network, triggering a sync cycle, and verifying that all accumulated events are ingested on the server exactly once.

**Acceptance Scenarios**:

1. **Given** a device without an active internet connection, **When** application activity occurs, **Then** events are persisted to the secure local database and flagged as pending synchronization.
2. **Given** accumulated offline records, **When** network connectivity is restored and a background synchronization cycle runs, **Then** pending records are batched, transmitted, acknowledged by the server, and marked as synchronized locally.
3. **Given** a network interruption during batch upload, **When** the synchronization is retried, **Then** the server detects previously ingested records by their client UUIDs, skips duplicate insertion, and returns an acknowledgment so the client clears its local buffer.

---

### User Story 4 - Goal Setting & App Usage Guardrails (Priority: P2)

As a user striving to reduce excessive phone use, I want to set daily screen time targets and specific duration limits for distracting applications so that I can monitor my discipline and receive visual alerts when nearing or exceeding my thresholds.

**Why this priority**: Self-monitoring is most effective when paired with actionable intentions and goal tracking. This enables users to translate awareness into behavioral modification.

**Independent Test**: Can be verified by creating a 30-minute daily goal for a specific social media app on the web dashboard, accumulating usage on the mobile device, synchronizing, and confirming that progress bars, threshold status indicators, and limit alerts update accurately.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the web dashboard, **When** they configure a daily screen time ceiling of 3 hours, **Then** the dashboard displays real-time progress toward that goal with color-coded status indicators (on-track, caution, exceeded).
2. **Given** a configured app limit, **When** the user's synchronized usage for that app surpasses the limit, **Then** the web dashboard highlights the violation in daily summaries and historical reports.
3. **Given** a configured app limit, **When** an application usage limit is reached on a mobile device, **Then** iOS enforces a native application shield via `ManagedSettings` where permitted, and Android issues a high-priority system notification with an in-app reminder overlay upon launch, with violation occurrences synchronized to the web dashboard.

---

### User Story 5 - AI-Powered Habit Insights & Recommendations (Priority: P3)

As a user seeking to improve my digital lifestyle, I want an intelligent assistant to analyze my weekly usage patterns, identify unhealthy habits (such as late-night scrolling or rapid multitasking), and offer personalized, realistic recommendations.

**Why this priority**: Raw statistics tell users *what* happened, but AI-driven interpretations explain *patterns* and deliver actionable guidance tailored to individual habits, dramatically enhancing long-term engagement and wellbeing outcomes.

**Independent Test**: Can be verified by triggering an insight generation request for a user account with at least one week of synchronized history, confirming that the AI service analyzes aggregated metrics and returns coherent, contextual advice without ingesting raw personal messages or device identifiers.

**Acceptance Scenarios**:

1. **Given** at least 3 days of recorded usage, **When** the user navigates to the AI Insights tab on the web dashboard, **Then** the system presents structured takeaways highlighting peak usage windows, fastest-growing app categories, and unusual habit shifts.
2. **Given** recurring late-night screen activity (between 11 PM and 4 AM), **When** weekly insights are generated, **Then** the system provides constructive guidance focused on sleep hygiene and digital wind-down routines.
3. **Given** privacy constraints, **When** the AI engine evaluates user habits, **Then** only anonymized, aggregated daily metrics and category totals are transmitted to the external intelligence provider.

---

### User Story 6 - Supported Network Usage Visibility (Priority: P3)

As a user on a metered data plan or interested in device resource footprint, I want to observe how much mobile data and Wi-Fi my device consumes where the operating system supports such measurement, while understanding any platform limitations where it is not available.

**Why this priority**: Network consumption often correlates with high-bandwidth background apps or passive streaming, providing complementary insight into digital usage patterns.

**Independent Test**: Can be verified by running the collector on an Android device with active network traffic, synchronizing data, and verifying that Wi-Fi vs. cellular usage values appear on the web dashboard, while testing on iOS displays a transparent "Not supported on this platform" indicator.

**Acceptance Scenarios**:

1. **Given** an Android device with permitted network access, **When** network statistics are synchronized, **Then** the web dashboard displays total and application-wise data transferred, partitioned by transmitted (Tx) and received (Rx) bytes across Wi-Fi and mobile data.
2. **Given** an iOS device, **When** the user navigates to the network analytics section, **Then** the dashboard displays an informational banner explaining that per-app network tracking is restricted by Apple operating system policies, without showing misleading zero values.

---

### User Story 7 - Privacy Control, Data Export & Account Deletion (Priority: P1)

As a privacy-conscious individual, I want full transparency and sovereignty over my personal activity data, including the ability to review what has been recorded, download my complete history, or permanently delete all my stored records and account.

**Why this priority**: Digital usage telemetry is intensely personal. Trust and regulatory compliance (GDPR/CCPA) require uncompromising user consent, transparent auditability, and irrevocable deletion guarantees.

**Independent Test**: Can be verified by submitting an export request, verifying that a structured data file is generated, and subsequently submitting an account deletion request, verifying that all associated device, session, summary, and user records are completely erased from the central database.

**Acceptance Scenarios**:

1. **Given** an authenticated user in account settings, **When** they click "Export My Data", **Then** the system compiles all historical usage sessions, daily summaries, and device registrations into a downloadable JSON/CSV archive.
2. **Given** an authenticated user, **When** they confirm account deletion with password verification, **Then** all personal profile data, device pairings, usage events, summaries, and AI insights are permanently purged from persistent storage.
3. **Given** a user revokes tracking consent from the mobile companion, **When** the app detects revocation, **Then** background data collection immediately ceases and the server is notified to halt pending ingestion.

---

### Edge Cases

- **Extended Offline Duration**: When a device remains disconnected for multiple days or weeks, local storage MUST buffer events up to a maximum retention limit of 30 days or 50,000 events. If storage limits are reached, acknowledged records are pruned first, followed by FIFO rollover of oldest events with a user notification to reconnect.
- **AI Service Availability & Minimum Data**: When an account has fewer than 3 days of recorded usage, the AI insights service returns a structured informational state explaining that additional activity data is needed before habit analysis can begin. If external Gemini API calls fail or timeout, the web dashboard displays a graceful retry banner without disrupting core analytics.
- **Timezone Transitions & Daylight Saving Time**: When a user travels across timezones or encounters DST transitions, raw timestamps stored in UTC must not drift or generate overlapping sessions; daily summaries must recalculate according to the active local calendar day.
- **Mid-Session Permission Revocation**: If a user disables Usage Access or Screen Time permissions in system settings while the app is backgrounded, the collector must detect the loss of permission gracefully, pause collection, and notify the user on the next app open without crashing.
- **Aggressive OS Process Termination**: Mobile operating systems (e.g., aggressive battery optimizers on OEM Android builds) may terminate background jobs; scheduled tasks must employ standard platform persistent job schedulers to restart collection upon next device unlock or power event.
- **Simultaneous Multi-Device Ingestion**: When a user registers multiple active phones or tablets, ingestion pipelines must handle concurrent batch synchronization without deadlock, partitioning records accurately by device identifier while maintaining an aggregate user-level view.
- **Clock Tampering / Device Skew**: If a user manually alters device time to bypass limits or game habits, the ingestion pipeline must validate event timestamps against server reception windows and monotonic sequence counters to discard anomalous time jumps.
- **High-Frequency App Switching**: Rapid switching between apps in under two seconds must be debounced or collapsed into valid foreground session intervals to avoid overwhelming storage with micro-events.

---

## Requirements *(mandatory)*

### Functional Requirements

#### 1. Device Registration & User Consent
- **FR-001**: System MUST allow users to register an account with email and password, authenticated via secure industry-standard tokens.
- **FR-002**: Mobile companion MUST register each physical device under the authenticated user account with a unique device identifier and platform metadata (OS type, OS version, app version).
- **FR-003**: Mobile companion MUST require explicit user consent and provide clear, plain-language disclosures before initiating any background telemetry collection.
- **FR-004**: System MUST record the timestamp and version of user consent in the database and immediately halt data collection if consent is revoked.

#### 2. Mobile Activity & Screen Time Data Collection
- **FR-005**: Mobile companion MUST operate as a lightweight background collector on supported versions of Android (8.0+) and iOS (16.0+).
- **FR-006**: Mobile companion MUST compute foreground application sessions bounded by explicit application foreground and background events OR device screen lock/off events; brief system interruptions or switches under 2 seconds MUST be debounced to preserve session continuity without false fragmentation.
- **FR-007**: Mobile companion MUST track device screen-on, screen-off, and device unlock events. Total daily screen time MUST be calculated strictly as the cumulative duration of active, unlocked physical screen-on states; individual application foreground session durations MUST be tracked and presented as sub-allocations within that total without duplicating or inflating the headline screen time.
- **FR-008**: Android integration MUST request and verify `PACKAGE_USAGE_STATS` (Usage Access) via standard platform interfaces.
- **FR-009**: iOS integration MUST request and verify Screen Time authorizations using official Apple frameworks (`FamilyControls` / `DeviceActivity`) without attempting unauthorized private API access.

#### 3. Network Usage Tracking
- **FR-010**: Mobile companion MUST collect daily uploaded and downloaded bytes (Tx and Rx) per application on Android platforms, partitioned distinctly by Wi-Fi and mobile data.
- **FR-011**: System MUST present an explicit "Platform Restricted" notice on the web dashboard for iOS devices regarding network telemetry, avoiding any display of unverified zero values.
- **FR-012**: System MUST NEVER report missing or unsupported platform metrics as zero consumption.

#### 4. Offline Storage & Resilient Synchronization
- **FR-013**: Mobile companion MUST store all captured activity records locally in an embedded persistent database prior to network transmission, maintaining an offline buffer capacity of up to 30 days or 50,000 events with deterministic FIFO pruning.
- **FR-014**: Mobile companion MUST batch pending local records and opportunistically synchronize with the backend service during network availability and background execution windows.
- **FR-015**: Backend service MUST support idempotent synchronization by indexing client-assigned event UUIDs; retransmitted batches or duplicate event UUIDs MUST be acknowledged as successful while skipping redundant ingestion, preventing inflated usage metrics.
- **FR-016**: Mobile companion MUST mark local records as synchronized only after receiving explicit positive acknowledgment from the backend service.

#### 5. Web Analytics & Usage Visualization
- **FR-017**: Web dashboard MUST display a comprehensive daily overview featuring total screen time, active app count, screen unlock count, and top-used applications.
- **FR-018**: Web dashboard MUST provide interactive daily, weekly, and monthly analytics views with visual representations of usage trends.
- **FR-019**: System MUST calculate all calendar-day usage summaries according to the user's configured IANA timezone while maintaining underlying event records in UTC.
- **FR-020**: Web dashboard MUST allow users to switch between an aggregated multi-device view and individual device views.
- **FR-021**: Web dashboard MUST categorize applications (e.g., Productivity, Social, Entertainment, Utilities) and display category distribution percentages.

#### 6. Usage Goals & App Limits
- **FR-022**: System MUST allow users to configure daily total screen-time duration goals on the web dashboard.
- **FR-023**: System MUST allow users to set specific daily duration limits for individual applications.
- **FR-024**: Web dashboard MUST visualize current progress against goals and limits with clear visual threshold indicators.
- **FR-025**: System MUST enforce application limits using platform-maximal capabilities: on iOS, trigger native application shielding via Apple `ManagedSettings` framework when authorized; on Android, trigger high-priority system notifications and warning reminder overlays; web dashboard MUST record and display all violation events in historical performance summaries.

#### 7. AI-Powered Habit Insights
- **FR-026**: System MUST generate personalized usage insights and recommendations using the Google Gemini service.
- **FR-027**: AI processing pipeline MUST ingest only aggregated usage summaries, category totals, and temporal trend metrics—never raw device telemetry, user identifiers, or personal communications.
- **FR-028**: System MUST produce structured habit assessments identifying peak usage windows, rapid category spikes, and potential night-time screen disruptions; if external AI service calls fail or timeout, the system MUST log the failure and return a recoverable error state for the client without crashing.
- **FR-029**: Web dashboard MUST display historical AI insights and allow users to view actionable suggestions for digital habit improvement; if fewer than 3 days of historical summaries exist, the system MUST display an informative onboarding placeholder prompt.

#### 8. Privacy, Security & Data Lifecycle
- **FR-030**: System MUST enforce strict user-level data isolation, ensuring users can only access their own devices and usage telemetry.
- **FR-031**: System MUST NEVER collect, inspect, or store notification contents, text messages, browsing contents, keystrokes, or screen captures.
- **FR-032**: All data in transit between mobile companion, backend service, and web dashboard MUST be encrypted using TLS/HTTPS.
- **FR-033**: System MUST provide a self-service data export function requiring authenticated session and password re-verification, allowing users to securely download their complete activity history in standard JSON format.
- **FR-034**: System MUST provide an irrevocable account deletion function that permanently purges user profile data, device associations, raw events, aggregated summaries, and generated insights within 5 seconds of confirmation.

---

### Key Entities

- **User**: Represents the account owner. Contains identity attributes, email, hashed credentials, timezone, and account lifecycle timestamps.
- **Registered Device**: Represents a physical smartphone running the mobile companion. Associated with a User; contains unique device token, platform type (Android/iOS), OS version, and last-seen synchronization timestamp.
- **Consent Record**: Represents an audit log of user consent for telemetry tracking. Contains User identifier, Device identifier, consent scope, policy version, and granted/revoked timestamps.
- **Application Catalog Item**: Represents an application detected on a user's device. Contains package/bundle identifier, user-friendly display name, assigned category, and optional icon metadata.
- **Raw Usage Event**: Represents an atomic foreground activity transition or screen state toggle. Contains client-generated UUID, Device identifier, application identifier, start timestamp (UTC), end timestamp (UTC), and calculated duration.
- **Usage Session**: Processed, contiguous interval of application foreground activity bounded by app lifecycle or device screen-off/lock states, with sub-2-second interruptions debounced.
- **Daily Usage Summary**: Pre-computed aggregation of total screen time, app-wise durations, unlock counts, and session counts for a given user, device, and local calendar date.
- **Network Usage Measurement**: Recorded volume of network data transferred (uploaded Tx and downloaded Rx bytes) per application and interface type (Wi-Fi vs. mobile data) on supported platforms (Android).
- **Usage Goal**: User-defined target for overall screen time or category allowance over a specific timeframe (e.g., daily max 3 hours).
- **Application Limit**: User-defined duration threshold for a specific application within a 24-hour cycle.
- **AI Insight**: Structured analytical report produced by Gemini containing summary findings, pattern detections, and recommended habit improvements.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete mobile companion installation, sign-in, and permission onboarding in under 2 minutes.
- **SC-002**: Mobile companion battery consumption MUST NOT exceed 3% of total battery discharge over a standard 24-hour measurement window under typical device usage.
- **SC-003**: Mobile companion application package size MUST remain below 35 MB on both Android (APK/AAB) and iOS (IPA) release builds.
- **SC-004**: 100% of activity records collected during offline periods are successfully synchronized without data corruption or duplicate counting once connectivity is restored.
- **SC-005**: Daily screen time and application usage durations calculated by the platform MUST demonstrate at least 98% accuracy when benchmarked against native operating system device reports.
- **SC-006**: Web dashboard overview page MUST achieve a First Contentful Paint (FCP) of under 1.5 seconds and display complete daily charts in under 2.0 seconds on standard broadband connections.
- **SC-007**: Synchronization API endpoints MUST process and acknowledge standard multi-event batches from client devices in under 500 milliseconds under normal operating loads.
- **SC-008**: 100% of associated personal data, device links, raw telemetry, summaries, and AI insights are permanently purged within 5 seconds of a confirmed account deletion request.
- **SC-009**: At least 85% of survey-sampled active users agree that AI-generated weekly insights provide actionable and relevant suggestions for their digital wellbeing.

---

## Assumptions

- **Target Operating Systems**: Devices run modern mobile operating systems: Android 8.0 (API level 26) or newer; iOS 16.0 or newer. Older platform versions lacking stable background usage APIs are out of scope.
- **Personal Scope**: The system is designed strictly for individual self-management. Multi-user administrative hierarchies, parental surveillance, and enterprise employee monitoring are explicitly excluded.
- **Operating System Policy Boundaries**: Background execution and telemetry collection remain subordinate to platform vendor policies. On iOS, screen-time reports and restrictions rely entirely on Apple's Screen Time framework and entitlement availability; network telemetry on iOS cannot be extracted per-app via public APIs.
- **Connectivity Model**: Devices have access to intermittent or continuous Wi-Fi or cellular data connectivity. Continuous real-time streaming of telemetry is not required; opportunistic batch synchronization is the standard operating model.
- **Web Dashboard Access**: Users access the analytical dashboard using standard evergreen desktop or tablet web browsers (Google Chrome, Apple Safari, Mozilla Firefox, Microsoft Edge).
- **AI Scope**: AI capabilities are purely analytical and advisory; AI services do not execute automated device actions or enforce device lockdowns directly.
