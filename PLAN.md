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
  * [x] Install Alembic: `uv add alembic`.
  * [x] Initialize migration files: `alembic init migrations`.
  * [x] Configure autogenerate metadata to map `SQLModel.metadata` and read the connection string from `settings.database_url`.
  * [x] Generate the initial schema migration script.
  * [x] Configure the startup script / Docker runner to execute `alembic upgrade head`.

---

## Phase 3: CI/CD & Database Divergence Testing
* **Objective:** Ensure dialect compatibility between the SQLite development environment and PostgreSQL production database.
* **Tasks:**
  * [x] Update GitHub Actions workflow (`ci.yml`) to run a PostgreSQL service container.
  * [x] Run the pytest suite against both SQLite (in-memory) and the PostgreSQL container to detect syntax or locking differences before pull requests are merged.

---

## Phase 4: Scalable Asynchronous Ingestion
* **Objective:** Decouple HTTP ingestion from measurement parsing and database writes to prevent timeouts and database lock contention.
* **Tasks:**
  * [x] Refactor `/webhook` route to return `202 Accepted` immediately (<10ms).
  * [x] Set up an asynchronous task processor (using FastAPI `BackgroundTasks`) to process records in the background.

---

## Phase 5: API Versioning & UI i18n
* **Objective:** Future-proof custom user integrations and prepare UI layouts for multi-language support.
* **Tasks:**
  * [x] Separate developer and app integrations onto a versioned router structure (e.g., `/api/v1/metrics`, `/api/v1/entries`).
  * [x] Integrate a translation helper (like `Babel` / `gettext`) to manage English and German localization strings.

---

## Phase 6: Advanced Clean Architecture & SOLID Abstractions
* **Objective:** Elevate codebase patterns to support enterprise-grade isolation, testability, and transactional safety.
* **Tasks:**
  * [x] **Repository Protocol Abstraction (DIP):** Define `typing.Protocol` interfaces for all repositories (e.g. `IUserRepository`). Services must type-hint against these interfaces rather than concrete SQLModel implementations, enabling database-agnostic operations.
  * [x] **Unit of Work Pattern (Transactional Atomicity):** Implement a Unit of Work context manager that orchestrates repositories and manages commit/rollback boundaries across multiple tables. This prevents inconsistent states (e.g. creating a user but failing to save their credentials leaving orphaned rows).
  * [x] **Request-Aware Exception Handling:** Refactor custom exception handlers in `main.py` to dynamically inspect incoming headers. Return structured `JSONResponse` payloads for `/api/...` endpoints and standard `HTMLResponse` or HTTP redirects for browser/HTMX requests.

---

# Visionary Product Roadmap: The Sovereign Health Platform

Salus is designed to give users complete sovereignty over their health data. Unlike proprietary silos, Salus prioritizes open APIs, decentralized communication, and user privacy.

## Phase 7: Sovereign Features & Ecosystem

### 1. Developer Sandbox & Plugin System [x]
* **Concept:** Create a plugin architecture allowing third-party developers to package custom data sources, parse custom export types, and render custom dashboard widgets.
* **Architecture:** Use a dynamic loader (or a sandboxed WASM runtime like `wasmtime`) to execute plugins without compromising core database safety. Expose a unified Python hook registry for extension registration.

### 2. Private, Local LLM Integration (Health Insights) [x]
* **Concept:** Run a private health coach directly on the user's system to generate insights based on logged sleep, nutrition, and workout metrics.
* **Architecture:** Integrate with local runtimes (e.g., Ollama or in-browser WebLLM) using local APIs. **Zero health data ever leaves the user's local infrastructure.**

### 3. Instance Federation & User Sharing [x]
* **Concept:** Allow decentralized instances of Salus and local multi-tenancy users to communicate. Users can securely share health metrics (e.g. daily steps or raw logs) with family members, friends, or doctors.
* **Architecture:** Developed a multi-tenant aware user-to-user sharing system. Local users are resolved directly via `@username`, and remote users via `@username:domain`. Implemented the `SharingRelationship` database schema, a granular sharing policy service, dynamic HTML checkboxes dashboard with inline policy options, and a secure bearer-token federated API.

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

### 15. Decoupled Data Storage (Solid Pod Integration)
* **Concept:** Decouple Salus entirely from a local SQLite/PostgreSQL database. Users can store all their health logs in a personal, decentralized "Solid Pod" (compliant with the W3C Social Linked Data specification).
* **Architecture:** Implement a WebID-OIDC login flow and write measurements using RDF graphs directly to the user's Solid Pod. Salus becomes a thin visualization/analytics app, while the user maintains absolute control over where the physical data files reside.

### 16. Direct BLE Device Ingestion (No Cloud Bridge)
* **Concept:** Ingest data directly from physical health devices (e.g. smart scales, blood pressure monitors, continuous glucose monitors - CGMs) over Bluetooth Low Energy (BLE), without registering accounts on manufacturers' proprietary clouds.
* **Architecture:** Utilize the browser's Web Bluetooth API (or native BLE APIs in the companion app) to connect, parse standard BLE GATT service profiles (like Pulse Oximeter, Weight Scale, and Heart Rate profiles), and save metrics directly.

### 17. High-Resolution Print-Ready PDF Reports
* **Concept:** Export medical-grade, clean PDF summaries of specific health logs (e.g., a 3-month blood pressure or blood glucose diary) that the user can print out or hand directly to their physician.
* **Architecture:** Implement print-specific styles via CSS media queries (`@media print`) and vector-based SVG rendering. Users can print directly from the browser's native print handler (or save as PDF) with zero server-side compilation dependencies.

### 18. Privacy-Preserving Federated Learning (Collaborative Research)
* **Concept:** Train medical anomaly prediction models (e.g. sleep apnea or arrhythmia detection) collectively across decentralized Salus nodes without ever pooling raw, private user data.
* **Architecture:** Utilize a federated learning framework (such as Flower or PySyft). Instances train a shared model on local data and only transmit encrypted model parameter updates (gradients) using Secure Multi-Party Computation (SMPC) or Homomorphic Encryption.

### 19. Smart Medication Safety & Interaction Logger
* **Concept:** Log medication intake alongside vitals, with an offline-first interaction warnings checker.
* **Architecture:** Download local, lightweight drug-interaction tables (such as OpenFDA mappings). The app automatically alerts the user if a food log (e.g., grapefruit juice) or a biometric alert (e.g., resting heart rate falling below 50 bpm while taking beta-blockers) poses a contraindication risk.

### 20. Verifiable Health Credentials (W3C Decoupled Passes)
* **Concept:** Store cryptographically verifiable health proofs (such as vaccination status, PCR tests, or lab reports) locally on Salus, sharing them via a QR code with third parties without revealing any other medical history.
* **Architecture:** Implement the W3C Verifiable Credentials (VC) standard, verifying signatures using DID (Decentralized Identifier) registries.

### 21. Zero-Knowledge Proofs for Health Insurance Compliance
* **Concept:** Prove to health insurance providers or corporate wellness programs that you meet activity thresholds (e.g. "average > 8,000 steps per day over 90 days") without disclosing actual raw logs, location coordinates, or time-series data.
* **Architecture:** Generate a Zero-Knowledge Range Proof (ZK-SNARK) locally in the client browser or app, validating the statement against the database hash. The provider verifies the cryptographic proof signature in milliseconds without accessing raw metrics.

### 22. Hardware-Attested Vitals (Anti-Spoofing Protocol)
* **Concept:** Prevent users from manually falsifying data (e.g. scripts forging 10,000 steps to trick insurance programs) in clinical trials or challenges.
* **Architecture:** Support cryptographically signed sensor packets at the hardware level (using Secure Enclaves on wearables). Salus validates the hardware key attestation before committing the data.

### 23. Biometric Cryptographic Seed Phrase Generation
* **Concept:** Use unique, stable physiological metrics (like heart rate variability signatures, EEG profiles, or micro-combinations of immutable biometric characteristics) to generate or recover cryptographic wallets/identities.
* **Architecture:** Utilize a fuzzy extractor algorithm to derive stable cryptographic key pairs from noisy biometric measurements.

### 24. Private Data Leasing Marketplaces (Micro-Monetization)
* **Concept:** Optionally monetize your health history by leasing it to clinical trials or pharmaceutical research, without selling or transferring the actual files.
* **Architecture:** Researchers dispatch containerized SQL queries to users' local Salus nodes. The query executes locally (in-situ compute), returns only the aggregated statistical result, and triggers a cryptocurrency micropayment (e.g., via the Lightning Network) directly to the user.

### 25. Epigenetic & Microbiome Tracking (Advanced Lab Data)
* **Concept:** Import and model raw DNA methylation data, epigenetic biological age indicators, and gut microbiome taxonomic sequencing reports locally.
* **Architecture:** Define database schemas for genomics and microbiome taxonomies. Build a local analytical service correlating daily lifestyle metrics (sleep, stress, nutrition) with biological clock offsets or bacterial diversity changes over time.

### 26. Homomorphic Encryption Queries (Cloud-Assisted Vitals Analytics)
* **Concept:** Compare individual health parameters against massive global cohort datasets (e.g., "compare my heart rate variability distribution with 1 million users") without revealing personal metrics to any cloud server.
* **Architecture:** Encrypt local datasets using homomorphic encryption schemas (like BGV or CKKS). A cloud node performs the aggregate calculations directly on the *encrypted data* without ever decrypting it, returning an encrypted result that only the user's private key can unlock.

### 27. Offline Emergency Medical NFC Pass (First Responder Attestation)
* **Concept:** Share critical emergency medical information (blood type, severe allergies, active prescriptions) securely with first responders offline, even if your phone is locked or out of battery.
* **Architecture:** Sync emergency profile subsets to passive NFC tags (wearables/cards) or static lock screen QR codes, signed with the user's private key and verifiable via a public first-responder app.

### 28. Smart Home Circadian Loop (Matter/Hue Actuation)
* **Concept:** Automatically tune home lighting (brightness, color temperature) dynamically in real-time based on your biological logs (sleep latency, wakefulness, logged stress indicators).
* **Architecture:** Build a service adapter communicating with local home automation hubs (like Home Assistant or Matter controllers) over local network sockets to actuate lights based on biometric state changes.

### 29. Zero-Knowledge Allergy Proofs for Restaurants
* **Concept:** Present proof of severe food allergies or medical dietary requirements (like celiac disease) to dining venues without exposing other private medical documents or identity details.
* **Architecture:** Generate a ZK-proof of allergy verification (signed originally by a certified laboratory) displayed via QR code, allowing the restaurant to verify the validity of the lab certificate signature without revealing user identity.

### 30. Local Clinical Trial Matching (Zero-Surveillance Recruitment)
* **Concept:** Participate in clinical trials without enrolling in centralized patient databases.
* **Architecture:** Clinical researchers publish trial criteria (e.g., "resting HR > 80 bpm, age 30-40, sleep efficiency < 75%"). The matching algorithm runs entirely on the user's local instance. If a match is found, the user receives an alert and can opt-in to establish direct encrypted contact.

### 31. SMPC Cohort Challenges (Zero-Sharing leaderboards)
* **Concept:** Host fitness leaderboards or challenges with friends, without any participant sharing their daily step counts or activity details with anyone else.
* **Architecture:** Implement Secure Multi-Party Computation (SMPC) protocols. The group's instances cooperatively compute the winner, averages, and rankings in-browser or on-node, revealing only the final leaderboard order without revealing the underlying raw metrics of any single user.

### 32. HL7 FHIR Patient Record Ingest
* **Concept:** Import medical records directly from hospital patient portals or laboratory exports (e.g., blood test panels, imaging summaries, vaccination schedules) and visualize them alongside lifestyle vitals.
* **Architecture:** Implement a local HL7 FHIR JSON schema parser. The app maps standard FHIR resource models (like Observation and DiagnosticReport) to Salus measurement types.

### 33. Local HRV Spectral Analysis (ANS Autonomic Nervous System Mapping)
* **Concept:** Map your autonomic nervous system stress response (sympathetic fight-or-flight vs. parasympathetic rest-and-digest balance) over time using heart rate variability.
* **Architecture:** Implement local frequency-domain spectral analysis (RMSSD, SDNN, LF/HF ratio calculations) on raw inter-beat interval (IBI) data. Provide localized recommendations (e.g., box-breathing prompts) when rolling sympathetic dominance rises.

### 34. Social Recovery of Encryption Keys (Shamir's Secret Sharing)
* **Concept:** Recover your private Salus encryption key if you lose your password/device, without relying on a centralized cloud recovery database.
* **Architecture:** Split the master decryption key into cryptographic shares using Shamir's Secret Sharing Scheme (e.g., 3-out-of-5 shares). Distribute the shares to trusted guardians (friends' Salus instances or secondary devices). Reconstruct the master key when a threshold of guardians approve.

### 35. Voice-to-Metrics Local AI Intake (Speech-to-Log)
* **Concept:** Log measurements, water intake, or foods hands-free using voice commands (e.g., "I just drank a glass of water and ran 5 kilometers"), processed entirely locally.
* **Architecture:** Package a lightweight Speech-to-Text and Named Entity Recognition (NER) pipeline (such as Whisper-tiny and a custom transformer compiled to WASM/ONNX). Extraction happens locally on device, creating structured log records immediately.

### 36. Citizen Science Study Execution (Decentralized Trials)
* **Concept:** Allow users to opt into health and epidemiological studies run by public universities or researchers, where raw data never leaves the user's host.
* **Architecture:** Researchers publish queries mapping specific metrics. The cohort results are aggregated using Local Differential Privacy (LDP) or Secure Multi-Party Computation (SMPC), returning only the anonymized, aggregated cohort stats to the study authors.

### 37. Local Computer Vision Posture & Gait Analyzer
* **Concept:** Analyze squat form, workout execution, running gait, or daily sitting posture via device camera video feeds without sending any video data to the cloud.
* **Architecture:** Implement browser-side body-tracking networks (e.g., MediaPipe or TensorFlow.js Pose Detection). Video feeds are processed entirely in local RAM and discarded immediately, logging only posture angle trends.

### 38. Real-Time HRV Resonance Biofeedback
* **Concept:** Guide users through resonant breathing exercises to achieve optimal autonomic nervous system balance (heart coherence) using real-time pulse data.
* **Architecture:** Establish a local Web Bluetooth connection with a chest strap or pulse oximeter. Render real-time HRV spectral shifts and breathing pacing cues, graphing heart coherence metrics dynamically on the dashboard.

### 39. Cross-Border Sovereign Medical Passport (DID-Compliant)
* **Concept:** Present an internationally recognized, cryptographically secure digital medical travel pass containing verified translations of vaccinations, chronic conditions, and active prescriptions.
* **Architecture:** Format credentials to be fully compliant with decentralized identity standards (such as W3C DIDs and verifiable credentials), signed by accredited medical institutions and readable via standardized offline QR code scans.

### 40. Local Private Genomic Risk Engine (Genomic Privacy)
* **Concept:** Calculate polygenic risk scores for lifestyle-modifiable conditions (e.g., cardiovascular disease risk, type-2 diabetes) by matching raw DNA data files (such as 23andMe exports) against open scientific databases, without uploading genetic code to any server.
* **Architecture:** Process raw genomic text files entirely in-browser/on-device, cross-referencing SNPs (Single Nucleotide Polymorphisms) with local indexes of scientific risk publications.

### 41. Metabolic Digital Twin (Local Predictive Simulation)
* **Concept:** Build a local metabolic simulator that projects how weight, biological age, and cardiorespiratory health will adapt under hypothetical changes (e.g., shifts in caloric macros or activity levels).
* **Architecture:** Implement rolling mathematical models (differential equations using SciPy) that fit historical biometrics to metabolic curves.

### 42. Decentralized ZK Organ Donor Registry
* **Concept:** Express and store organ donor preferences locally, generating a verifiable token that emergency responders can inspect without storing your preferences in a centralized government database.
* **Architecture:** Generate a ZK-proof of registration signed by the user's DID, readable offline via QR scans.

### 43. ZK Sports & Event Clearance (Doctor Certificates)
* **Concept:** Register for sports events (e.g. marathons) proving you have medical cardiac clearance and are of required age, without revealing your actual medical records or date of birth.
* **Architecture:** Generate client-side ZK-proofs verifying "age > 18" and "certified cardiac clearance within 6 months" based on lab-signed credentials.

### 44. Local Private Vaccine & Immunization Scheduler
* **Concept:** Track immunizations and receive optimal booster alerts offline, based on national vaccination rules, without registering with external trackers.
* **Architecture:** Package an offline rules engine cross-referencing user ages and immunization histories.

### 45. Blinded Vitals Auditing (Anonymized Compliance Proofs)
* **Concept:** Prove compliance with physical rehabilitation or medication schedules to auditors (e.g. employers or insurers) using cryptographically blinded vitals reports.
* **Architecture:** Apply blinding factor keys to database records so auditors verify signature authenticity without identifying the user.











