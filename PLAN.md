# Salus Development Plan & Architecture Roadmap

This document serves as the central log of completed architectural refactorings and the roadmap for upcoming development phases.

---

## Phase 1: Completed Optimizations & Performance Refactoring

### 1. Progressive Widget Rendering (HTMX Lazy-Loading)
* **What we did:** Decoupled the main dashboard grid rendering from measurement data retrieval. The grid now loads instantly (~10ms) showing pulsing card skeletons with titles, and triggers concurrent backend requests (`hx-trigger="load"`) to populate each widget asynchronously.
* **Why we did it:** Eliminated perceived dashboard load delays, prevented Layout Shift (CLS), and separated slow widget queries from layout rendering.

### 2. Webhook Ingestion Resolution Cache
* **What we did:** Implemented request-level resolution caching (in-memory memoization) inside `MetricTypeMappingService`.
* **Why we did it:** Fixed an N+1 query bottleneck where importing large webhook sync payloads (e.g. 5,000 heart rate records) caused 5,000 identical database queries to look up mapping IDs. Ingestion is now O(1) per unique data type.

### 3. Named Dependency Factories
* **What we did:** Refactored anonymous lambda expressions inside `Depends()` declarations in `dependencies.py` to clean, named factory functions (`get_api_token_repo`, `get_api_token_service`).
* **Why we did it:** Restored proper Pyright/mypy static type checking, aligned with the project's dependency inversion standard, and enabled simple mock overrides in test suites.

### 4. Base Repository Batch Actions
* **What we did:** Added `add()`, `add_all()`, and `commit()` methods to the base `Repository` class to allow deferring transaction commits.
* **Why we did it:** Enabled services to stage bulk updates and commit exactly once, removing the SQL execution lockups caused by executing commits in loops.

### 5. Analytics Range Queries
* **What we did:** Redesigned `steps_trend` and `heart_rate_ohlc` in `ActivityAnalysisService` to query their entire timeline ranges (e.g., 7 or 30 days) using **exactly one query**, performing data grouping in Python memory.
* **Why we did it:** Eliminated N+1 daily looping database queries on historical trends.

---

## Phase 2: Schema Migrations (Alembic)
* **Objective:** Introduce versioned database migrations to protect user data and manage schema changes over time.
* **Tasks:**
  * [ ] Install Alembic: `uv add alembic`.
  * [ ] Initialize migration files: `alembic init migrations`.
  * [ ] Configure autogenerate metadata to map `SQLModel.metadata` and read the connection string from `settings.database_url`.
  * [ ] Generate the initial schema migration script.
  * [ ] Configure the startup script / Docker runner to execute `alembic upgrade head`.

---

## Phase 3: CI/CD & Database Divergence Testing
* **Objective:** Ensure dialect compatibility between the SQLite development environment and PostgreSQL production database.
* **Tasks:**
  * [ ] Update GitHub Actions workflow (`ci.yml`) to run a PostgreSQL service container.
  * [ ] Run the pytest suite against both SQLite (in-memory) and the PostgreSQL container to detect syntax or locking differences before pull requests are merged.

---

## Phase 4: Scalable Asynchronous Ingestion
* **Objective:** Decouple HTTP ingestion from measurement parsing and database writes to prevent timeouts and database lock contention.
* **Tasks:**
  * [ ] Refactor `/webhook` route to save incoming raw payload JSON to a dedicated `raw_ingestion_buffer` table and return `202 Accepted` immediately (<10ms).
  * [ ] Set up an asynchronous task processor (using FastAPI `BackgroundTasks` or a background runner like `taskiq` / `rq`) to process buffer records in the background.

---

## Phase 5: API Versioning & UI i18n
* **Objective:** Future-proof custom user integrations and prepare UI layouts for multi-language support.
* **Tasks:**
  * [ ] Separate developer and app integrations onto a versioned router structure (e.g., `/api/v1/metrics`, `/api/v1/entries`).
  * [ ] Integrate a translation helper (like `Babel` / `gettext`) to manage English and German localization strings.

---

## Phase 6: Advanced Clean Architecture & SOLID Abstractions
* **Objective:** Elevate codebase patterns to support enterprise-grade isolation, testability, and transactional safety.
* **Tasks:**
  * [ ] **Repository Protocol Abstraction (DIP):** Define `typing.Protocol` interfaces for all repositories (e.g. `IUserRepository`). Services must type-hint against these interfaces rather than concrete SQLModel implementations, enabling database-agnostic operations.
  * [ ] **Unit of Work Pattern (Transactional Atomicity):** Implement a Unit of Work context manager that orchestrates repositories and manages commit/rollback boundaries across multiple tables. This prevents inconsistent states (e.g. creating a user but failing to save their credentials leaving orphaned rows).
  * [ ] **Request-Aware Exception Handling:** Refactor custom exception handlers in `main.py` to dynamically inspect incoming headers. Return structured `JSONResponse` payloads for `/api/...` endpoints and standard `HTMLResponse` or HTTP redirects for browser/HTMX requests.

