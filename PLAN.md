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

---

# Visionary Product Roadmap: The Sovereign Health Platform

Salus is designed to give users complete sovereignty over their health data. Unlike proprietary silos, Salus prioritizes open APIs, decentralized communication, and user privacy.

## Phase 7: Sovereign Features & Ecosystem

### 1. Developer Sandbox & Plugin System
* **Concept:** Create a plugin architecture allowing third-party developers to package custom data sources, parse custom export types, and render custom dashboard widgets.
* **Architecture:** Use a dynamic loader (or a sandboxed WASM runtime like `wasmtime`) to execute plugins without compromising core database safety. Expose a unified Python hook registry for extension registration.

### 2. Private, Local LLM Integration (Health Insights)
* **Concept:** Run a private health coach directly on the user's system to generate insights based on logged sleep, nutrition, and workout metrics.
* **Architecture:** Integrate with local runtimes (e.g., Ollama or in-browser WebLLM) using local APIs. **Zero health data ever leaves the user's local infrastructure.**

### 3. Instance Federation (Peer-to-Peer Sync)
* **Concept:** Allow decentralized instances of Salus to communicate. Users can sync data across devices (e.g. laptop and server) or securely share anonymized metrics (like step-challenge rankings) with friends across different self-hosted servers.
* **Architecture:** Implement an E2E-encrypted sync protocol (using WebDAV or custom HTTPS endpoints) and a lightweight federated protocol (inspired by ActivityPub or WebSub) to securely transmit metrics.

### 4. Offline-First Mobile/Desktop App
* **Concept:** Build a cross-platform companion app (e.g., using Tauri, Flutter, or React Native) that runs offline-first.
* **Architecture:** Keep a local SQLite database on the client device that auto-syncs securely with the primary Salus instance when connected to the local Wi-Fi or internet.

### 5. Smart Workout & Training Planner
* **Concept:** Implement a workout generator and tracker that dynamically adjusts sets, reps, and target weights based on logged recovery metrics (e.g. sleep duration, resting heart rate, and steps trend).
* **Architecture:** Build an exercise registry model and a custom service that maps workouts, tracking fatigue indexes in-memory.

### 6. Zero-Knowledge E2E Encrypted Backups
* **Concept:** Provide automated, encrypted backups to user-owned storage providers (Nextcloud, Proton Drive, WebDAV, or local backups).
* **Architecture:** Encrypt SQL dumps on the fly with user-provided AES keys before uploading, ensuring the hosting provider has zero knowledge of the raw health data.

### 7. Asymmetric Encrypted Doctor Sharing (GP Integration)
* **Concept:** Allow users to temporarily and securely share specific health dashboards directly with their general practitioner (GP) or personal trainer.
* **Architecture:** Use public/private key cryptography (Web Crypto API directly in the browser). The user encrypts selected date ranges using the recipient's public key. The recipient decrypts it locally. No unencrypted data is ever visible on the server.

### 8. Statistical Data Synthesizer (Open Science)
* **Concept:** Enable users to donate their health data to medical research anonymously.
* **Architecture:** Build an in-memory generation pipeline that synthesizes data matching the user's exact trends and distributions (using differential privacy), allowing researchers to use the statistical properties without accessing personal metrics.

### 9. Circadian Rhythm & Light Advisor
* **Concept:** Provide optimal sleep window, meal timing, and wind-down advice based on geographical sunrise/sunset calculations, ambient light measurements, and core biometric logs.
* **Architecture:** Build a mathematical model analyzing sleep depth offsets relative to light exposure patterns.

### 10. Zero-Knowledge Peer Challenges (ZKP Gamification)
* **Concept:** Engage in fitness challenges (e.g. "Who hits 15k steps first") without uploading raw logs to a central tracker.
* **Architecture:** Generate cryptographically signed step receipts on device, and use Zero-Knowledge Proofs (ZKP) to prove compliance with a threshold (e.g., proving "steps > 15,000" without revealing the exact step count, GPS location, or timeframe).

### 11. Multi-Device Sync CRDTs (Conflict Resolution)
* **Concept:** Keep data completely consistent when the user logs health metrics offline on multiple devices (e.g., laptop and smartphone) and syncs later.
* **Architecture:** Implement Conflict-Free Replicated Data Types (CRDTs), specifically LWW-Element-Set (Last-Write-Wins-Element-Set) or delta-state CRDTs. This resolves merge conflicts deterministically without requiring a central server coordinator or losing historical log changes.

### 12. Local AI Food Photo Parser (Private Nutritionist)
* **Concept:** Log meals and calculate macronutrients (carbs, protein, fats) automatically by taking a photo of a meal, without sending the image to proprietary cloud vision APIs.
* **Architecture:** Embed lightweight image-classification and object-detection models (like YOLOv8 or MobileNet-V3) compiled to WebAssembly (WASM) or executed locally on-device using ONNX Runtime. All image processing is fully local.

### 13. Environmental & Biometric Correlation (Local OpenData)
* **Concept:** Correlate cardiorespiratory and recovery vitals (resting heart rate, blood oxygen saturation, sleep stages) with external environmental parameters (pollen counts, particulate matter PM2.5/PM10, temperature, and humidity).
* **Architecture:** Fetch environmental metrics from public, open-source APIs (such as Open-Meteo) based on user-defined regional coordinates, calculating Pearson correlation coefficients locally.

### 14. Biometric Anomaly Detection (Early Warning System)
* **Concept:** Automatically detect and notify the user of statistical anomalies in their recovery vitals, serving as an early indicator of viral infection, acute physical strain, or overtraining.
* **Architecture:** Implement local statistical modeling (e.g., standard deviation thresholding or rolling Z-scores) on resting heart rate, HRV, and sleep depth to flag abnormal deviation spikes over 3+ consecutive days.




