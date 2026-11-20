# Data Model Specification: Digital Wellbeing Platform

**Feature**: `001-digital-wellbeing-platform` | **Date**: 2026-11-20

This document defines the relational database schema, entities, relationships, validation constraints, and indexing strategy for the PostgreSQL database.

---

## 1. Entity Relationship Overview

```text
       +------------------+
       |      users       |
       +--------+---------+
                | 1
                |
                +-------------------+--------------------+--------------------+
                |                   |                    |                    |
                | *                 | *                  | *                  | *
       +--------v---------+ +-------v--------+ +---------v--------+ +---------v--------+
       |     devices      | |  user_consents | |   usage_goals    | |   user_insights    |
       +--------+---------+ +----------------+ +------------------+ +------------------+
                | 1
                |
       +--------+--------------------+--------------------+--------------------+
       |                             |                    |                    |
       | 1                           | *                  | *                  | *
+------v--------------+    +---------v--------+ +---------v--------+ +---------v--------+
| device_capabilities |    | app_usage_events | | screen_activity  | |  network_usage   |
+---------------------+    +------------------+ +------------------+ +------------------+
                                     |
                                     | (Aggregated into)
                                     v
                           +------------------+
                           |  daily_summaries |
                           +---------+--------+
                                     | 1
                                     | *
                           +---------v--------+
                           | app_daily_summ.  |
                           +------------------+
```

---

## 2. Table Specifications

### 2.1 Identity, Authentication & Consent

#### `users`
Represents the registered user account.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Unique user identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email address (lowercased) |
| `password_hash` | VARCHAR(255) | NOT NULL | Argon2id/bcrypt salted password hash |
| `timezone` | VARCHAR(64) | NOT NULL, DEFAULT 'UTC' | User's IANA timezone (e.g., 'America/New_York') |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active status |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last profile modification timestamp |

#### `refresh_tokens`
Tracks rotating authentication refresh tokens.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Token record ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Associated user |
| `token_hash` | VARCHAR(255) | NOT NULL, UNIQUE | SHA-256 hash of refresh token |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Token expiration timestamp |
| `revoked` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token has been invalidated |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

#### `user_consents`
Audit log of explicit user consent for background data collection.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Consent audit record ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Associated user |
| `consent_type` | VARCHAR(64) | NOT NULL | Scope (e.g., 'USAGE_COLLECTION', 'AI_ANALYSIS') |
| `policy_version` | VARCHAR(32) | NOT NULL | Privacy policy version consented to |
| `granted` | BOOLEAN | NOT NULL | TRUE for grant, FALSE for revocation |
| `timestamp` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Timestamp of consent action |

---

### 2.2 Devices & Catalog

#### `devices`
Physical mobile devices running the companion collector.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Device ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Account owner |
| `device_identifier`| VARCHAR(128) | NOT NULL | Client-generated stable device UUID |
| `platform` | VARCHAR(16) | NOT NULL | 'android' or 'ios' |
| `device_model` | VARCHAR(128) | NOT NULL | e.g., 'Pixel 8', 'iPhone 15' |
| `os_version` | VARCHAR(32) | NOT NULL | e.g., 'Android 14', 'iOS 17.4' |
| `app_version` | VARCHAR(32) | NOT NULL | Version of the Flutter companion app |
| `last_sync_at` | TIMESTAMPTZ | NULL | Last successful synchronization timestamp |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Device registration timestamp |

*Index*: `UNIQUE (user_id, device_identifier)`

#### `device_capabilities`
Discovered platform feature support per device.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Record ID |
| `device_id` | UUID | NOT NULL, UNIQUE, FK -> devices(id) ON DELETE CASCADE | Target device |
| `supports_network_tracking` | BOOLEAN | NOT NULL | TRUE on Android, FALSE on iOS |
| `supports_app_shielding` | BOOLEAN | NOT NULL | TRUE on iOS Screen Time, FALSE on standard Android |
| `has_usage_permission` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether Android Usage Access is active |
| `has_screen_time_permission`| BOOLEAN | NOT NULL, DEFAULT FALSE | Whether iOS Screen Time authorization is active |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last capability check timestamp |

#### `app_categories`
System catalog of application functional categories.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | SERIAL | PK | Category ID |
| `name` | VARCHAR(64) | NOT NULL, UNIQUE | Category name (e.g., 'Productivity', 'Social') |
| `color_hex` | VARCHAR(7) | NOT NULL | Hex color for dashboard charts (e.g., '#4F46E5') |

---

### 2.3 Raw Telemetry & Usage Ingestion

#### `app_usage_events`
Atomic raw foreground application intervals received from devices.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Event ID |
| `device_id` | UUID | NOT NULL, FK -> devices(id) ON DELETE CASCADE | Source device |
| `event_uuid` | UUID | NOT NULL | Client-generated event UUID for deduplication |
| `package_name` | VARCHAR(255) | NOT NULL | App identifier (e.g., 'com.google.android.youtube')|
| `start_time` | TIMESTAMPTZ | NOT NULL | UTC start timestamp |
| `end_time` | TIMESTAMPTZ | NOT NULL | UTC end timestamp |
| `duration_seconds`| INTEGER | NOT NULL | Computed duration in seconds |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Server ingestion timestamp |

*Constraints & Indexes*:
- `UNIQUE (device_id, event_uuid)` (Primary deduplication constraint)
- `INDEX idx_app_events_device_time (device_id, start_time)`
- `INDEX idx_app_events_package (package_name)`

#### `screen_activity_events`
Physical device screen power and unlock state transitions.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Screen event ID |
| `device_id` | UUID | NOT NULL, FK -> devices(id) ON DELETE CASCADE | Source device |
| `event_uuid` | UUID | NOT NULL | Client-generated event UUID |
| `event_type` | VARCHAR(32) | NOT NULL | 'SCREEN_ON', 'SCREEN_OFF', 'USER_UNLOCKED' |
| `timestamp` | TIMESTAMPTZ | NOT NULL | UTC timestamp of transition |

*Constraints & Indexes*:
- `UNIQUE (device_id, event_uuid)`
- `INDEX idx_screen_events_device_time (device_id, timestamp)`

#### `network_usage_events`
Available network data consumption measurements (Android only).
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Record ID |
| `device_id` | UUID | NOT NULL, FK -> devices(id) ON DELETE CASCADE | Source device |
| `event_uuid` | UUID | NOT NULL | Client-generated event UUID |
| `package_name` | VARCHAR(255) | NOT NULL | Application package identifier |
| `wifi_bytes_rx` | BIGINT | NOT NULL, DEFAULT 0 | Wi-Fi bytes received |
| `wifi_bytes_tx` | BIGINT | NOT NULL, DEFAULT 0 | Wi-Fi bytes sent |
| `mobile_bytes_rx`| BIGINT | NOT NULL, DEFAULT 0 | Cellular bytes received |
| `mobile_bytes_tx`| BIGINT | NOT NULL, DEFAULT 0 | Cellular bytes sent |
| `calendar_date` | DATE | NOT NULL | Measurement date in device local timezone |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Ingestion timestamp |

*Constraints & Indexes*:
- `UNIQUE (device_id, event_uuid)`
- `INDEX idx_network_device_date (device_id, calendar_date)`

---

### 2.4 Aggregations & Analytics

#### `daily_usage_summaries`
Pre-calculated summary of device usage for a specific calendar date in user timezone.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Summary ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | User ID |
| `device_id` | UUID | NOT NULL, FK -> devices(id) ON DELETE CASCADE | Device ID |
| `calendar_date` | DATE | NOT NULL | Local calendar date |
| `total_screen_time_seconds`| INTEGER | NOT NULL, DEFAULT 0 | Cumulative active unlocked duration |
| `total_unlocks` | INTEGER | NOT NULL, DEFAULT 0 | Count of device unlock events |
| `total_sessions`| INTEGER | NOT NULL, DEFAULT 0 | Count of discrete app sessions |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last aggregation recalculation |

*Constraints & Indexes*:
- `UNIQUE (user_id, device_id, calendar_date)`
- `INDEX idx_daily_summaries_user_date (user_id, calendar_date)`

#### `app_daily_summaries`
Per-application foreground allocation within a daily summary.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Record ID |
| `daily_summary_id`| UUID | NOT NULL, FK -> daily_usage_summaries(id) ON DELETE CASCADE | Parent daily summary |
| `package_name` | VARCHAR(255) | NOT NULL | Application package identifier |
| `total_foreground_seconds` | INTEGER | NOT NULL, DEFAULT 0 | Total active foreground seconds |
| `session_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of launches/sessions |

*Index*: `UNIQUE (daily_summary_id, package_name)`

---

### 2.5 Goals, Limits & Violations

#### `usage_goals`
User-defined goals for daily screen time or category limits.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Goal ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Target user |
| `target_type` | VARCHAR(32) | NOT NULL | 'TOTAL_SCREEN_TIME' or 'CATEGORY' |
| `category_id` | INTEGER | NULL, FK -> app_categories(id) | Associated category (if category goal) |
| `max_duration_seconds`| INTEGER | NOT NULL | Target daily threshold in seconds |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

#### `app_limits`
Threshold limits configured for individual applications.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Limit ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Target user |
| `package_name` | VARCHAR(255) | NOT NULL | Application package identifier |
| `max_duration_seconds`| INTEGER | NOT NULL | Daily limit in seconds |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active status |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

*Index*: `UNIQUE (user_id, package_name)`

#### `app_limit_violations`
Historical log of threshold breaches.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Violation record ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | User ID |
| `device_id` | UUID | NOT NULL, FK -> devices(id) ON DELETE CASCADE | Device where violation occurred |
| `package_name` | VARCHAR(255) | NOT NULL | Application package identifier |
| `violation_date` | DATE | NOT NULL | Date of breach |
| `actual_duration_seconds`| INTEGER | NOT NULL | Recorded duration at breach |
| `limit_duration_seconds` | INTEGER | NOT NULL | Configured limit threshold |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Logging timestamp |

---

### 2.6 AI Insights & Background Queue

#### `user_insights`
AI-generated habit assessments and recommendations.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Insight ID |
| `user_id` | UUID | NOT NULL, FK -> users(id) ON DELETE CASCADE | Target user |
| `insight_type` | VARCHAR(32) | NOT NULL | 'WEEKLY_SUMMARY', 'HABIT_ALERT', 'RECOMMENDATION' |
| `title` | VARCHAR(255) | NOT NULL | Headline title |
| `content` | TEXT | NOT NULL | Narrative explanation and advice |
| `structured_data`| JSONB | NOT NULL, DEFAULT '{}' | Pattern metadata, detected spikes, score |
| `wellbeing_score`| INTEGER | NULL | 1-100 normalized wellbeing index |
| `start_date` | DATE | NOT NULL | Start of analyzed window |
| `end_date` | DATE | NOT NULL | End of analyzed window |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Generation timestamp |

#### `app_tasks`
PostgreSQL-backed asynchronous job queue replacing Redis.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Task ID |
| `task_type` | VARCHAR(64) | NOT NULL | e.g., 'RECALCULATE_SUMMARIES', 'GENERATE_AI_INSIGHT' |
| `payload` | JSONB | NOT NULL, DEFAULT '{}' | Arguments for task execution |
| `status` | VARCHAR(16) | NOT NULL, DEFAULT 'PENDING' | 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED' |
| `scheduled_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Earliest execution time |
| `locked_until` | TIMESTAMPTZ | NULL | Concurrency lock timeout timestamp |
| `retry_count` | INTEGER | NOT NULL, DEFAULT 0 | Failed retry counter |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

*Index*: `INDEX idx_app_tasks_worker (status, scheduled_at)`
