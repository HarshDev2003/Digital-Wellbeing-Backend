<!--
# Sync Impact Report
- Version Change: Initial Template (0.0.0) -> 1.0.0
- Ratification Date: 2026-11-20
- Last Amended Date: 2026-11-20
- Principles Defined:
  - Replaced template placeholders with 15 Core Engineering Principles:
    1. Modular Monolith Architecture
    2. Unified Cross-Platform Mobile Application (Flutter)
    3. High-Performance Asynchronous Backend (Python FastAPI)
    4. PostgreSQL as the Single Source of Truth
    5. Zero-Redis Infrastructure Discipline
    6. Modern Web Analytics Dashboard (Next.js, React, TypeScript)
    7. Gemini API for AI-Powered Insights
    8. Lightweight Mobile Footprint and Dependency Hygiene
    9. Platform Abstraction and Isolation
    10. Platform Permission and API Compliance
    11. Security, Privacy by Design, and Data Deletion
    12. Clean Architecture and Consistent Conventions
    13. Rigorous Test Automation (Unit and Integration)
    14. Spec-First and Plan-Approved Engineering
    15. Simplicity and YAGNI Principle (You Aren't Gonna Need It)
- Added Sections:
  - Technical & Architectural Constraints
  - Development Workflow & Quality Gates
  - Governance
- Removed Sections:
  - Unused template placeholder comments and unfilled tokens
- Follow-up TODOs:
  - None. All tokens concretely defined.
-->

# Digital Wellbeing Constitution

## Core Principles

### 1. Modular Monolith Architecture
The backend application MUST be structured as a unified modular monolith. Domain boundaries (Authentication, Device Management, Usage Ingestion, Usage Processing, Network Usage, Analytics, Goals, App Limits, AI Insights, and Data Management) MUST be strictly preserved via explicit module contracts and interfaces. Microservices, distributed message buses, or independent service deployments are strictly prohibited unless ratified through formal constitutional amendment.
*Rationale: Minimizes distributed systems complexity, operational overhead, and network latency while providing maintainable, independently testable functional modules for personal usage tracking.*

### 2. Unified Cross-Platform Mobile Application (Flutter)
The mobile client for Android and iOS MUST be built from a single, shared Flutter/Dart codebase. Disparate native application repositories or cross-framework fragmentation are prohibited. The mobile application functions primarily as a lightweight background data collector and local cache client; full analytical reporting is delegated to the web dashboard.
*Rationale: Guarantees unified background synchronization semantics, simplifies release pipelines, and eliminates code duplication across mobile operating systems.*

### 3. High-Performance Asynchronous Backend (Python FastAPI)
The server-side service MUST be developed using Python and the FastAPI framework. All HTTP endpoints MUST adhere to RESTful conventions under `/api/v1` and utilize strict Pydantic schemas for request and response validation. Asynchronous I/O (`async`/`await`) MUST be used for database and external network interactions to maximize ingestion throughput.
*Rationale: Delivers high developer velocity, type safety, native asynchronous I/O for concurrent data synchronization, and standard compatibility with modern Python AI tooling.*

### 4. PostgreSQL as the Single Source of Truth
PostgreSQL MUST serve as the sole primary persistent datastore for all relational, raw usage event, session, summary, and user identity data. Primary keys MUST utilize UUIDs where appropriate. All timestamps MUST be captured in UTC with user IANA timezones stored separately for accurate local summary aggregation. Tables MUST enforce foreign keys and unique constraints to prevent ingestion duplicates.
*Rationale: Guarantees strict ACID transactions, reliable long-term auditability, and sophisticated indexing for time-series usage telemetry without multi-database synchronizations.*

### 5. Zero-Redis Infrastructure Discipline
Redis, external message brokers (such as RabbitMQ or Apache Kafka), and separate caching layers MUST NOT be introduced into the project infrastructure. Background processing and scheduled tasks MUST initially utilize FastAPI background tasks or database-backed task persistence in PostgreSQL. External caching MUST NOT be added until database query optimization and indexing have been exhausted and justified by measured performance bottlenecks.
*Rationale: Eliminates unnecessary hosting costs, reduces DevOps maintenance surface area, and prevents cache invalidation inconsistencies in personal habit tracking.*

### 6. Modern Web Analytics Dashboard (Next.js, React, TypeScript)
The web dashboard MUST be engineered using Next.js (App Router), React, and strict TypeScript. The web dashboard serves as the primary analytics and visualization interface for daily screen time, app breakdowns, network statistics, usage goals, and AI insights. It MUST communicate with the backend exclusively via authenticated REST API calls and MUST NOT connect directly to the database or device endpoints.
*Rationale: Offloads heavy charting, analytics visualization, and reporting interfaces from the mobile client to a responsive, accessible, and type-safe web platform.*

### 7. Gemini API for AI-Powered Insights
All generative digital wellbeing insights, usage pattern evaluations, and proactive recommendations MUST be powered by the Google Gemini API (orchestrated optionally with lightweight LangGraph workflows when multi-step structured reasoning is required). The backend AI module MUST only pass pre-aggregated, privacy-vetted usage summaries to Gemini—never raw personal telemetry, identifiers, or message contents.
*Rationale: Provides state-of-the-art behavioral habit analysis while protecting privacy through summary aggregation and isolating AI workflows from core data ingestion.*

### 8. Lightweight Mobile Footprint and Dependency Hygiene
The Flutter mobile application MUST maintain a minimal binary footprint and low runtime resource utilization (battery, CPU, and RAM). Heavy UI component packs, charting packages, local machine learning models, and superfluous graphic or font assets MUST NOT be bundled into the mobile app. Code shrinking, asset optimization, and clean dependency management MUST be enforced on all production release builds.
*Rationale: Background tracking services must remain unobtrusive, energy-efficient, and resilient against aggressive operating system background process termination.*

### 9. Platform Abstraction and Isolation
All native OS capabilities (Android `UsageStatsManager`, `NetworkStatsManager`, `WorkManager`; iOS `Screen Time`, `FamilyControls`, `DeviceActivity`) MUST be encapsulated behind strict Flutter platform interfaces. Shared Flutter business logic and UI code MUST NEVER directly couple to platform-specific APIs. Native implementations must reside in dedicated platform channels or isolated platform packages.
*Rationale: Enables independent platform evolution, deterministic mocking and test execution in CI/headless environments, and modular maintenance of OS-level permissions.*

### 10. Platform Permission and API Compliance
Applications MUST strictly respect platform-specific permission lifecycles and sandbox limitations. Android implementations must require explicit user authorization for Usage Access (`PACKAGE_USAGE_STATS`) and background execution. iOS implementations must strictly adhere to Apple's Screen Time framework entitlements and limitations. Missing platform capabilities (such as per-app network tracking on iOS) MUST be handled gracefully as platform-dependent rather than reported as zero or treated as systemic failures.
*Rationale: Guarantees app store compliance, prevents permission crashes, respects user device autonomy, and avoids invalid assumptions across operating systems.*

### 11. Security, Privacy by Design, and Data Deletion
System design MUST follow privacy-by-design principles:
- Authentication MUST use secure industry standards (JWT with robust secret handling and salted cryptographic password hashing).
- Sensitive communication content, notifications, keystrokes, and message payloads MUST NEVER be captured or stored.
- Explicit, auditable user consent MUST be recorded prior to data collection.
- Users MUST have the capability to export their full usage history and permanently delete their accounts and all associated data on demand.
- All API communication MUST enforce HTTPS/TLS.
*Rationale: Establishes foundational user trust and complies with international data privacy regulations (GDPR, CCPA).*

### 12. Clean Architecture and Consistent Conventions
All repositories and modules MUST adhere to Clean Architecture principles. Layers (Presentation, Application/Domain, and Data/Infrastructure) MUST be strictly separated, with dependencies pointing inward toward domain abstractions. Codebases MUST follow unified conventions:
- Python: PEP 8, snake_case for functions and variables, PascalCase for classes, typed Pydantic models.
- Dart / Flutter: Effective Dart guidelines, camelCase for members, PascalCase for types.
- TypeScript / Next.js: camelCase for variables/functions, PascalCase for React components and types.
*Rationale: Eliminates structural rot, fosters code discoverability, and ensures frictionless navigation across the full technology stack.*

### 13. Rigorous Test Automation (Unit and Integration)
Automated testing is mandatory across all layers:
- Business logic, session duration calculations, timezone adjustments, and aggregation logic MUST have comprehensive unit tests (using `pytest` for backend, `flutter_test` for mobile, and modern test runners for web).
- All backend REST endpoints, authentication barriers, and synchronization pipelines MUST have automated integration tests validating database persistence and idempotent deduplication.
*Rationale: Prevents functional regressions, guarantees mathematical precision in usage summaries, and guarantees safe continuous integration.*

### 14. Spec-First and Plan-Approved Engineering
No feature development, structural refactoring, or external interface alteration may proceed without an approved Product Requirements/Technical Specification and a phased, reviewed implementation plan. Code contributions written without prior specification approval MUST NOT be merged.
*Rationale: Eliminates scope creep, prevents architectural divergence across mobile, web, and backend, and ensures that every pull request maps directly to defined product goals.*

### 15. Simplicity and YAGNI Principle (You Aren't Gonna Need It)
Engineers MUST rigorously reject unwarranted complexity. Every added third-party library, infrastructure component, or architectural abstraction must be justified against explicit requirements in `doc/PRD.md` and `doc/TSD.md` (or canonical `docs/PRD.md` and `docs/TECH_SPEC.md`). If a simpler native solution suffices, it MUST be chosen over introducing external dependencies.
*Rationale: Reduces attack surfaces, minimizes maintenance debt, speeds up onboarding, and ensures the product remains lean and dependable.*

## Technical Constraints & Infrastructure Boundaries

1. **Approved Technology Stack**:
   - Mobile: Flutter (Dart) with native platform channels (Android: Kotlin / WorkManager / UsageStats; iOS: Swift / FamilyControls / DeviceActivity).
   - Backend: Python 3.11+ / FastAPI / Pydantic / SQLAlchemy or SQLModel / Alembic.
   - Database: PostgreSQL (Single persistent instance, UTC storage, indexed by user/device/timestamp).
   - Web Frontend: Next.js (App Router), React, TypeScript, Tailwind CSS.
   - AI Services: Google Gemini API (structured prompt engineering and optional LangGraph orchestrator).
   - Cloud & Hosting: Containerized via Docker; reverse-proxied via Nginx; targeted for AWS deployment.

2. **Prohibited Infrastructure**:
   - Redis or in-memory key-value stores.
   - Distributed messaging brokers (Kafka, RabbitMQ, SQS) in initial architecture.
   - Multi-database or NoSQL datastores.
   - Direct database access from frontend or mobile clients.

3. **Data & Synchronization Guarantees**:
   - Mobile data synchronization MUST be offline-first, storing events locally before opportunistic transmission.
   - Data ingestion endpoints MUST be idempotent using client-generated event UUIDs or batch deduplication identifiers.
   - Aggregate screen time and application foreground usage must be calculated distinctly from screen-on events.

## Development Workflow & Quality Gates

1. **Specification Alignment**:
   All engineering tasks must align strictly with the approved product requirements (`doc/PRD.md` / `docs/PRD.md`) and technical specifications (`doc/TSD.md` / `docs/TECH_SPEC.md`).
2. **Quality Gates Before Merge**:
   - Clean linting and static analysis across all codebases (e.g., `ruff`/`flake8` for Python, `flutter analyze` for Flutter, `eslint` for TypeScript).
   - Unit tests passing with high coverage on business calculations.
   - Integration tests passing against PostgreSQL for synchronization routes.
   - Absence of unapproved dependencies or architecture-violating imports.
3. **Security Checkpoints**:
   - No hardcoded secrets, API tokens, or private credentials in version control.
   - Verified authentication middleware on all private endpoints.
   - User-isolation filters on all database queries (preventing multi-tenant or cross-user data leakage).
4. **Implementation Track Phasing**:
   - The current active implementation in this repository is strictly focused on the Backend Modular Monolith (FastAPI, PostgreSQL, Task Queue, Gemini AI service, and RESTful APIs).
   - The Flutter mobile companion application and Next.js web dashboard are specified for architectural alignment and contract parity, but are implemented separately in dedicated client development tracks.

## Governance

1. **Constitutional Supremacy**:
   This constitution defines the non-negotiable architectural laws and engineering standards for the Digital Wellbeing project. It supersedes informal agreements, ad-hoc developer preferences, and non-canonical documentation.
2. **Amendment Procedure**:
   Any modification, addition, or removal of principles requires:
   - A documented architectural decision record (ADR) justifying the change.
   - An impact analysis on existing mobile, backend, and frontend subsystems.
   - Formal consensus and sign-off.
   - A corresponding semantic version bump of this constitution.
3. **Versioning Policy**:
   This document follows Semantic Versioning (`MAJOR.MINOR.PATCH`):
   - **MAJOR**: Removals, redefinitions, or backward-incompatible shifts in core governance or architecture (e.g., introducing microservices or changing the primary database).
   - **MINOR**: Additions of new principles, structural sections, or materially expanded technical constraints.
   - **PATCH**: Wording improvements, typography, clarifications, and non-semantic refactorings.
4. **Compliance Enforcement**:
   Every code review and pull request MUST explicitly verify adherence to this constitution. Any deviation without an approved amendment MUST result in a request for changes.

**Version**: 1.0.1 | **Ratified**: 2026-11-20 | **Last Amended**: 2026-11-21
