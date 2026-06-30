# Project Brief: Salus Health Intelligence

## 1. Executive Summary
Salus is a personal health data platform designed to aggregate, store, and visualize biometric data from diverse health sources (starting with Samsung Health Connect). It provides a browser-based, high-fidelity dashboard for managing health metrics, tracking long-term goals, and performing deep analytics on physiological trends.

## 2. Product Vision & Goals
- **Data Centralization**: Aggregate fragmented health data into a single, user-owned repository.
- **Actionable Insights**: Move beyond raw data to provide correlations (e.g., sleep vs. activity).
- **Clinical Precision**: Maintain high data integrity for medical or professional review.
- **Privacy First**: Secure, multi-user architecture with localized data management.

## 3. Target Audience
- **Health-Conscious Individuals**: Users tracking fitness, sleep, or nutrition for personal optimization.
- **Patients/Clinical Users**: Individuals monitoring specific health metrics (SpO2, HR) for medical oversight.
- **Quantified Self Enthusiasts**: Power users who value raw data access and export capabilities.

## 4. Technical Architecture
### Core Stack
- **Backend**: FastAPI (Python 3.13+)
- **Templates**: Jinja2 (Server-side rendering)
- **Interactivity**: HTMX 2.x (Zero-JS-framework philosophy)
- **Database**: Dual-SQLite strategy
    - `salus.db`: Application state and user-scoped CRUD (SQLModel).
    - `health.db`: High-throughput, raw JSON ingestion pipeline (sqlite3).
- **Environment**: Nix flake for reproducible development.

### Key Architectural Decisions
- **Dependency Inversion**: Strict 4-layer architecture (Router → Service → Repository → DB).
- **Protocol-Based Parsers**: Extensible parser system for multi-source ingestion (Samsung, Apple Health, Oura).
- **Constructor Injection**: All services are testable with mock repositories.

## 5. Feature Roadmap

### Phase 1: Foundation (Completed)
- Dashboard with CRUD for metric types and entries.
- Samsung Health Connect webhook ingestion.
- Multi-format payload parsing logic.

### Phase 2: Multi-User & Auth (In Progress)
- JWT-based authentication (Register/Login).
- User-scoped data associations for all entries and metrics.
- Secure session management via cookies/Bearer tokens.

### Phase 3: Analytics & Intelligence
- **Visualizations**: Time-series charts for Weight, Steps, HR, and Sleep.
- **Metabolic Baseline**: TDEE calculation via Cunningham Formula.
- **Anomalies**: SpO2 monitoring and low-value alerts.
- **Exercise History**: Support for 84+ exercise types with duration/distance metrics.

### Phase 4: Goals & Tracking
- Goal definition (Target value, Frequency, Deadline).
- Progress calculation and visual "On Track/Missed" statuses.
- Automated email/in-app alerts for goal verifications.

### Phase 5: Advanced Features
- **Data Portability**: CSV/JSON export and REST API access.
- **Integrations**: Apple Health, Google Fit, Fitbit, and Oura Ring.
- **PWA**: Offline support and mobile homescreen installation.

## 6. Design Philosophy
- **Unified Aesthetic**: Professional, clinical-grade interface using the Manrope typeface and Indigo (#4f46e5) accents.
- **Layout**: Full-width (1200px max) card-based layouts for maximum data density and readability.
- **Navigation**: Simplified top-navigation bar for streamlined cross-view access.
- **Responsiveness**: Flex-based layouts to support various desktop and tablet viewports.

## 7. Success Metrics
- **Reliability**: Zero data loss during high-throughput ingestion.
- **Performance**: Dashboard load times under 200ms (leveraging SQLite + HTMX).
- **Engagement**: Frequency of goal check-ins and analytics interaction.
