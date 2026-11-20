# Product Requirements Document (PRD)
## Digital Wellbeing

### 1. Product Overview

**Digital Wellbeing** is a personal digital activity tracking platform that helps users understand and manage their mobile usage.

The platform collects mobile activity data from Android and iOS devices and displays it through a centralized web dashboard. It provides screen-time analytics, app-wise usage, network usage (where supported), usage goals, app limits, and AI-powered insights.

### 2. Product Objectives

- Track daily mobile screen time.
- Monitor app-wise usage and activity.
- Track mobile network usage where supported by the operating system.
- Understand daily, weekly, and monthly digital habits.
- Set screen-time goals and app usage limits.
- Provide AI-powered recommendations to improve digital wellbeing.

### 3. Target Users

- Individual users managing their own digital habits.
- Personal use only; family and organization management are outside the initial scope.

### 4. Core Features

#### 4.1 Mobile Data Collection

Android and iOS mobile applications will collect permitted device activity data in the background.

- Screen-time tracking.
- App-wise usage duration.
- App launch and session activity.
- Device activity information.
- Network usage, subject to operating system capabilities.
- Background data synchronization with the backend.

**Note:** Android and iOS have different permissions and APIs. Some app-level usage and network metrics may not be available on both platforms.

#### 4.2 Web Dashboard

The web dashboard will provide:

- Total daily screen time.
- App-wise usage breakdown.
- Daily, weekly, and monthly reports.
- Most-used applications.
- Usage trends and activity summaries.
- Network usage overview.
- Device information and synchronization status.

#### 4.3 Usage Goals

- Set daily screen-time goals.
- Set individual app usage targets.
- Monitor progress against goals.
- View goal completion history.

#### 4.4 App Limits

- Configure usage limits for selected applications.
- Monitor applications exceeding their limits.
- Apply app restrictions where supported by the operating system and required permissions.

#### 4.5 AI-Powered Insights

- Analyze screen-time patterns.
- Identify frequently used applications.
- Highlight excessive usage patterns.
- Provide personalized recommendations.
- Generate daily and weekly activity summaries.

### 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system must collect mobile usage data from supported devices. |
| FR-02 | The system must synchronize collected data with the backend. |
| FR-03 | Users must be able to view total screen time. |
| FR-04 | Users must be able to view app-wise usage. |
| FR-05 | Users must be able to view network usage where supported. |
| FR-06 | Users must be able to view historical usage reports. |
| FR-07 | Users must be able to configure usage goals. |
| FR-08 | The system must support app usage limits where permitted. |
| FR-09 | The system must generate AI-based usage insights. |
| FR-10 | Users must be able to manage their device connection and collected data. |

### 6. Non-Functional Requirements

- Secure authentication and data storage.
- Privacy-focused data collection with user consent.
- Efficient background data collection and synchronization.
- Support offline data storage and later synchronization.
- Responsive web dashboard.
- Reliable handling of large usage histories.
- User control over data retention and deletion.

### 7. Technology Overview

| Component | Proposed Technology |
|---|---|
| Android App | Kotlin |
| iOS App | Swift / SwiftUI |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| Cache / Background Jobs | Redis |
| Web Dashboard | Next.js / React / TypeScript |
| AI Integration | Gemini API |
| AI Workflow (optional) | LangGraph |
| Deployment | AWS |

### 8. Project Scope

**Included**
- Android and iOS mobile data collectors.
- Centralized backend and database.
- Web-based personal dashboard.
- Screen-time and app-wise analytics.
- Network usage tracking where supported.
- Usage goals and app limits where supported.
- AI-powered insights and reports.

**Not Included in Initial Scope**
- Family accounts and parental controls.
- Organization or employee monitoring.
- Social features and user-to-user sharing.
- Public mobile applications for other users.

### 9. Expected Outcome

A personal digital wellbeing platform that provides a clear understanding of mobile usage, helps identify unhealthy usage patterns, and supports better digital habits through analytics, goals, app limits, and AI-powered recommendations.