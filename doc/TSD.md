# Technical Specification Document (TSD)
## Digital Wellbeing

**Version:** 1.0  
**Document Type:** Technical Specification  
**Architecture:** Modular Monolith  
**Target Platforms:** Android, iOS and Web

---

## 1. Project Overview

Digital Wellbeing is a personal digital activity tracking platform that collects mobile usage information and presents it through a centralized web dashboard.

Users can monitor screen time, app-wise usage, network consumption, usage trends, goals, and AI-generated insights.

The mobile application will be developed using Flutter to support Android and iOS from a shared codebase.

The backend will use Python FastAPI with PostgreSQL. The web dashboard will use Next.js and React.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Mobile Application | Flutter / Dart |
| Android Platform Integration | Native Android APIs through Flutter platform integration |
| iOS Platform Integration | Apple Screen Time APIs through Flutter platform integration |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Web Dashboard | Next.js / React / TypeScript |
| AI Integration | Gemini API |
| AI Workflow | LangGraph, if required |
| Authentication | JWT-based authentication |
| Deployment | AWS |
| Web Server | Nginx |
| Containerization | Docker |

**Architecture decision:** Redis is excluded. PostgreSQL will be the primary persistent data store. Background processing will initially use FastAPI background tasks or a lightweight database-backed job mechanism where needed.

## 3. System Architecture

The system will follow a modular monolithic architecture.

### 3.1 High-Level Architecture

```text
                 MOBILE APPLICATION
                    Flutter App
                         |
             -------------------------
             |                       |
       Android APIs              iOS APIs
       Usage Stats             Screen Time APIs
       Network Stats           Available Reports
             |                       |
             -------------------------
                         |
                  Local Storage
                         |
                   Data Sync
                         |
                         v
                 FASTAPI BACKEND
                         |
       -------------------------------------
       |          |          |             |
   Auth Module  Device    Usage       Analytics
                Module   Module        Module
       |          |          |             |
       -------------------------------------
                         |
                    PostgreSQL
                         |
              ---------------------
              |                   |
         AI Insights         Reporting APIs
              |                   |
           Gemini API              |
              |                   |
              ---------------------
                         |
                         v
                 NEXT.JS DASHBOARD
```

### 3.2 Architecture Principles

- Keep the backend as one deployable application.
- Separate business logic into independent modules.
- Use a shared Flutter codebase for Android and iOS.
- Store mobile data locally before synchronization.
- Keep the backend independent of mobile platform-specific APIs.
- Use PostgreSQL as the central source of truth.
- Keep AI processing separate from core usage tracking.
- Minimize third-party dependencies and application size.

## 4. Mobile Application Specification

### 4.1 Flutter Application

The Flutter application will primarily work as a background data collector.

Its main responsibilities are:

1. Obtain required user permissions.
2. Collect permitted device activity data.
3. Store collected data locally.
4. Synchronize pending records with the backend.
5. Handle offline scenarios.
6. Provide basic permission and synchronization status.

The initial mobile application will not contain a complete analytics dashboard. Analytics will be available through the web dashboard.

### 4.2 Mobile Modules

| Module | Responsibility |
|---|---|
| Permission Manager | Request and check platform permissions |
| Usage Collector | Collect app usage and screen activity |
| Network Collector | Collect available network usage statistics |
| Local Database | Store collected activity data |
| Sync Manager | Synchronize records with backend |
| Device Manager | Register and identify devices |
| Background Scheduler | Schedule collection and synchronization |
| Platform Integration | Communicate with native Android and iOS APIs |

### 4.3 Android Data Collection

Android integration will use platform APIs through Flutter platform channels or carefully selected Flutter plugins.

Required capabilities:

- UsageStatsManager for application usage statistics.
- UsageEvents for application foreground and background events.
- NetworkStatsManager for available network consumption statistics.
- WorkManager for scheduled background tasks.
- Local database for offline records.

Required permissions and access:

- Usage access permission.
- Network-related permissions where required.
- Background execution permissions and appropriate platform configuration.

The user must explicitly grant usage access where required.

### 4.4 iOS Data Collection

iOS integration will use Apple's Screen Time framework APIs where available.

Relevant frameworks:

- FamilyControls
- DeviceActivity
- ManagedSettings
- DeviceActivityReport

Potential capabilities:

- Screen-time reporting.
- Application activity reports.
- App restrictions through supported APIs and entitlements.

**Important:** Apple's Screen Time APIs require appropriate authorization and entitlements. Some functionality may require native iOS extensions. Flutter cannot bypass these restrictions.

Per-app network usage and unrestricted background collection are not generally available through public iOS APIs. Therefore, network tracking must be treated as platform-dependent.

### 4.5 Lightweight Application Requirement

The Flutter application must be optimized for a small installation size.

Technical guidelines:

- Use only necessary Flutter packages.
- Avoid large UI and charting libraries in the mobile app.
- Keep analytics and AI processing on the backend.
- Do not bundle machine learning models in the mobile application.
- Avoid unnecessary image, animation, and font assets.
- Use release builds with code shrinking and asset optimization where applicable.
- Use deferred components or other platform-supported optimization only when justified.
- Avoid unnecessary background services and excessive polling.

The final application size will be measured using release builds for Android and iOS. A target size should be established after the first prototype because native platform integrations and operating-system packaging affect the final size.

## 5. Backend Specification

### 5.1 FastAPI Backend

The backend will be implemented as a modular monolith.

Responsibilities:

- User authentication.
- Device registration.
- Usage data ingestion.
- Data validation and deduplication.
- Usage session processing.
- Network usage storage.
- Analytics and reporting.
- Goal management.
- AI insight generation.
- User and device data management.

### 5.2 Backend Modules

| Module | Responsibility |
|---|---|
| Authentication | Registration, login, JWT and token validation |
| User Management | User profile and account settings |
| Device Management | Device registration and synchronization status |
| Usage Ingestion | Receive and validate mobile activity records |
| Usage Processing | Process app sessions and daily summaries |
| Network Usage | Store and aggregate available network statistics |
| Analytics | Generate daily, weekly and monthly reports |
| Goals | Create and track screen-time goals |
| App Limits | Manage supported app usage restrictions and settings |
| AI Insights | Generate personalized usage recommendations |
| Data Management | User consent, export and deletion operations |

### 5.3 Backend Processing Flow

1. Flutter collects device activity.
2. The mobile application saves records locally.
3. The Sync Manager sends pending records to FastAPI.
4. FastAPI validates the authentication and request payload.
5. The backend checks duplicate records.
6. Valid records are saved in PostgreSQL.
7. Usage processing generates sessions and daily summaries.
8. Analytics APIs provide aggregated results.
9. AI services analyze selected usage summaries.
10. The web dashboard displays the results.

## 6. Database Specification

PostgreSQL will be the primary database.

### 6.1 Proposed Database Tables

| Table | Purpose |
|---|---|
| users | User account information |
| devices | Registered mobile devices |
| device_capabilities | Supported device features and permissions |
| user_consents | User permissions and consent history |
| app_categories | Application categories |
| installed_apps | Applications detected on devices |
| app_usage_events | Raw application activity events |
| usage_sessions | Processed application usage sessions |
| screen_activity_events | Screen activity events |
| network_usage_events | Available network usage measurements |
| daily_usage_summaries | Daily device usage summaries |
| app_daily_summaries | Daily application usage summaries |
| usage_goals | User-defined usage goals |
| user_insights | AI-generated insights |
| sync_batches | Mobile synchronization history |
| refresh_tokens | Authentication refresh tokens |
| audit_logs | Important system and account actions |

### 6.2 Database Design Principles

- Use UUID primary keys where appropriate.
- Store timestamps in UTC.
- Store the user's IANA timezone separately.
- Calculate daily summaries using the user's local timezone.
- Add indexes for user ID, device ID, application ID and event timestamps.
- Use unique identifiers to prevent duplicate event ingestion.
- Keep raw events separate from aggregated summaries.
- Define a data retention and deletion policy.

### 6.3 Important Data Distinctions

- Screen-on time and application foreground time must be calculated separately.
- Application usage should be based on valid foreground activity intervals.
- Network measurements must identify whether they represent Wi-Fi, mobile data or another available network category.
- Missing platform data must not be interpreted as zero usage.

## 7. API Specification

All backend APIs will use REST architecture and JSON responses.

Base path:

`/api/v1`

### 7.1 Authentication APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/register | Register user |
| POST | /auth/login | User login |
| POST | /auth/refresh | Refresh access token |
| POST | /auth/logout | Logout user |
| GET | /auth/me | Get authenticated user |

### 7.2 Device APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /devices/register | Register mobile device |
| GET | /devices | List user devices |
| GET | /devices/{id} | Get device details |
| PATCH | /devices/{id} | Update device information |
| DELETE | /devices/{id} | Remove device |

### 7.3 Usage APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /usage/sync | Upload usage records |
| GET | /usage/daily | Get daily usage |
| GET | /usage/apps | Get application-wise usage |
| GET | /usage/sessions | Get application sessions |
| GET | /usage/history | Get historical usage |

### 7.4 Network Usage APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /network/sync | Upload network statistics |
| GET | /network/daily | Get daily network usage |
| GET | /network/apps | Get application-wise network usage where available |
| GET | /network/history | Get historical network usage |

### 7.5 Analytics APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /analytics/overview | Dashboard overview |
| GET | /analytics/weekly | Weekly analytics |
| GET | /analytics/monthly | Monthly analytics |
| GET | /analytics/trends | Usage trends |
| GET | /analytics/top-apps | Most-used applications |

### 7.6 Goals and AI APIs

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /goals | Create usage goal |
| GET | /goals | List usage goals |
| PATCH | /goals/{id} | Update usage goal |
| DELETE | /goals/{id} | Delete usage goal |
| POST | /ai/insights/generate | Generate insights |
| GET | /ai/insights | Retrieve insights |
| GET | /ai/insights/{id} | Get insight details |

## 8. Web Dashboard Specification

The web dashboard will be the main user interface for understanding digital activity.

### 8.1 Dashboard Modules

| Module | Features |
|---|---|
| Overview | Total screen time, usage summary and key metrics |
| App Analytics | App-wise usage, top apps and categories |
| Network Analytics | Wi-Fi and mobile data usage where available |
| Reports | Daily, weekly and monthly reports |
| Usage Trends | Historical activity trends |
| Goals | Goal creation and progress tracking |
| App Limits | Configure supported application limits |
| AI Insights | Recommendations and activity summaries |
| Devices | Connected devices and synchronization status |
| Settings | Account, privacy and data management |

### 8.2 Dashboard Data Flow

The Next.js dashboard will communicate with FastAPI using authenticated REST APIs.

It will not directly access mobile device usage APIs or PostgreSQL.

## 9. AI Integration

Gemini API will be used for AI-powered insights.

### 9.1 AI Responsibilities

- Analyze daily usage summaries.
- Identify frequently used applications.
- Detect unusual increases in usage.
- Compare current and previous usage patterns.
- Generate weekly activity summaries.
- Recommend improvements to digital habits.

### 9.2 AI Processing Flow

```text
PostgreSQL Usage Summaries
          |
          v
    Analytics Service
          |
          v
     AI Insights Module
          |
          v
       Gemini API
          |
          v
    Structured Insights
          |
          v
     PostgreSQL
          |
          v
      Web Dashboard
```

AI will receive aggregated and minimized usage information rather than unnecessary raw device records.

## 10. Security and Privacy

- Use JWT-based authentication.
- Hash user passwords using a secure password hashing algorithm.
- Enforce user-level data access authorization.
- Use HTTPS for all API communication.
- Collect only data required for the application's functionality.
- Obtain explicit consent for sensitive usage access.
- Allow users to delete their accounts and associated data.
- Avoid collecting notification contents, messages or personal communication data.
- Secure API secrets and database credentials.
- Maintain audit logs for important account and data operations.

## 11. Synchronization and Background Processing

The mobile application must support offline-first data collection.

### Synchronization flow

1. Collect activity records.
2. Store records in the local database.
3. Identify records not yet synchronized.
4. Send records in batches to the backend.
5. Receive server acknowledgment.
6. Mark acknowledged records as synchronized.
7. Retry failed batches when connectivity is available.

The backend must support idempotent synchronization to avoid duplicate records.

Background synchronization is opportunistic. Android and iOS may delay scheduled background execution, so exact synchronization intervals cannot be guaranteed.

## 12. Development Phases

| Phase | Work | Expected Outcome |
|---|---|---|
| Phase 1 | Project setup, database design and authentication | Working backend foundation |
| Phase 2 | Flutter setup, permissions and Android usage collection | Android data collector |
| Phase 3 | iOS Screen Time integration and capability validation | iOS data collection prototype |
| Phase 4 | Usage ingestion, local storage and synchronization | End-to-end mobile data pipeline |
| Phase 5 | Analytics APIs and web dashboard | Screen-time and app-wise reports |
| Phase 6 | Network usage collection and reporting | Supported network analytics |
| Phase 7 | Goals and app limits | Digital wellbeing management |
| Phase 8 | Gemini AI integration | AI-generated insights |
| Phase 9 | Testing, optimization and AWS deployment | Initial production release |

## 13. Initial Release Acceptance Criteria

The first usable release should satisfy these conditions:

1. A user can register and log in.
2. A Flutter application can register a device.
3. The application can request and verify required permissions.
4. Supported mobile usage data can be collected.
5. Collected records can be stored locally.
6. Records can synchronize with FastAPI.
7. Duplicate synchronization does not create duplicate records.
8. The web dashboard can show daily screen time and app-wise usage.
9. Historical usage reports can be displayed.
10. Network usage is displayed only when reliable platform data is available.
11. AI insights can be generated from usage summaries.
12. The application is optimized for a small release size.

---

## 14. Final Architecture Decisions

| Decision | Final Selection |
|---|---|
| Product | Digital Wellbeing |
| Target users | Personal use |
| Mobile framework | Flutter |
| Backend | FastAPI |
| Architecture | Modular monolith |
| Database | PostgreSQL |
| Cache | No Redis |
| Web dashboard | Next.js |
| Authentication | Email and password |
| AI provider | Gemini |
| AI workflow | LangGraph if needed |
| Deployment | AWS |
| Mobile application role | Data collection |
| Main analytics interface | Web dashboard |
| Application optimization | Lightweight release build |

**Technical conclusion:** Digital Wellbeing will use a single Flutter codebase for mobile, a modular FastAPI backend, PostgreSQL for storage, and a Next.js web dashboard. The architecture prioritizes lightweight mobile installation, reliable data synchronization, privacy, and platform-specific capability handling.
