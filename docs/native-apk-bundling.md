# Salus — Native Android APK Bundling & Health Ecosystem Architecture

**Status**: Approved Architectural Specification  
**Date**: August 2026  
**Authors**: Core Architecture Team  
**Scope**: Capacitor Container, Health Connect API, Samsung Health SDK, Biometrics, KeyStore Security, and Build Toolchain

---

## 1. Executive Summary & Mission Statement

Salus is designed as a **Local-First Health Platform** utilizing FastAPI (backend), SvelteKit SPA (frontend), Dexie.js (IndexedDB storage), and SSE (Live Sync). 

To evolve Salus into a primary mobile health hub on Android, we require direct hardware access, background data harvesting from wearable sensors (e.g. Samsung Galaxy Watch, Oura, Garmin via Health Connect), biometric device protection, and 100% offline standalone execution.

This document specifies the architectural roadmap for packaging the Salus SvelteKit SPA into a native Android Application Package (APK) and Android App Bundle (AAB) using **Capacitor** as the native runtime shell.

---

## 2. Core Principles & Integration Mandate

Every native addition to Salus **MUST** strictly adhere to the project's core principles:

- **DRY (Don't Repeat Yourself)**: A single SvelteKit codebase target. Web browser and native APK share 100% of UI components, stores, state management, and IndexedDB schemas.
- **SOLID & DIP (Dependency Inversion)**: Native capabilities (Biometrics, Health Sync, Haptics) are accessed via abstract TypeScript interfaces. Web fallbacks (Web APIs / No-op) are injected when running in standard web browsers.
- **Local-First Single Source of Truth**: All native sensor data (steps, HR, sleep, BP, body composition) is ingested directly into Dexie IndexedDB as standard Salus `Measurement` rows via `mutate()`. The existing outbox sync engine pushes these entries to the FastAPI server transparently.
- **System Integration**: Native health data MUST integrate with:
  1. **Measurement System**: Automatic time-series writing with `source` attribution (e.g. `source="samsung_health"` or `source="health_connect"`).
  2. **Dashboard Widgets**: Sparklines, confidence bands, and trend widgets surface harvested data without UI modifications.
  3. **Analytics Engine**: Sleep, activity, and circadian analysis derive recovery scores from ingested native metrics.
  4. **Goals & Insights**: Automatic progress tracking against defined user goals.

---

## 3. Container Strategy: Capacitor vs. Trusted Web Activity (TWA)

We evaluated the two industry-standard approaches for wrapping PWAs into Android APKs:

| Feature / Criteria | Trusted Web Activity (TWA) | Capacitor Native Container (`@capacitor/android`) | **Salus Choice** |
|---|---|---|---|
| **Execution Engine** | Chrome Custom Tabs (Host Browser) | Android `WebView` (`android.webkit.WebView`) | **Capacitor** |
| **Asset Location** | Hosted on HTTPS Web Domain | Embedded locally in APK (`assets/public/`) | **Capacitor** |
| **Offline Independence** | Depends on Service Worker cache | **100% Standalone**, instant boot from disk | **Capacitor** |
| **Native Java/Kotlin Bridge** | Very limited (Web APIs only) | **Full Access** via Custom Java/Kotlin Plugins | **Capacitor** |
| **Samsung Health / Health Connect SDK** | Impossible (No native SDK binding) | **Direct Binding** via Java/Kotlin Capacitor Plugin | **Capacitor** |
| **App Store & F-Droid Compatibility** | Requires AssetLinks domain verification | **Standard Native APK / AAB** | **Capacitor** |

**Architectural Decision**: We select **Capacitor** because Salus requires direct access to native Java/Kotlin Android SDKs (Health Connect & Samsung Health Partner SDK) and must run 100% standalone from local APK assets even without initial network connectivity.

---

## 4. Native API Integration Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Salus SvelteKit SPA                               │
│                   (IndexedDB / Dexie.js / Svelte 5 Runes)                    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Abstract Native Bridge (DIP)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    Capacitor Native Android Container                       │
│                                                                             │
│  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────┐  │
│  │ Health Connect Plugin │ │ Samsung Health Plugin │ │ Biometrics Plugin │  │
│  │  (Standard Sensors)   │ │  (BIA / ECG / BP)     │ │ (KeyStore / Auth) │  │
│  └───────────┬───────────┘ └───────────┬───────────┘ └─────────┬─────────┘  │
└──────────────┼─────────────────────────┼───────────────────────┼────────────┘
               │                         │                       │
               ▼                         ▼                       ▼
    Android Health Connect      Samsung Health SDK        Android KeyStore &
     (Background Worker)        (Partner Privileged)      Hardware Biometrics
```

### A. Health Ecosystem Synchronization

Salus will implement a **Two-Tier Native Health Sync Architecture**:

#### Tier 1: Android Health Connect (`androidx.health.connect.client`)
- **Package**: `androidx.health.connect.client`
- **Gradle Dependency**: `implementation("androidx.health.connect:connect-client:1.1.0-alpha07")`
- **Supported Sensor Metrics**:
  - `StepsRecord` → `metric_code="steps"`
  - `HeartRateRecord` → `metric_code="heart_rate"`
  - `HeartRateVariabilityRmssdRecord` → `metric_code="hrv"`
  - `SleepSessionRecord` → `metric_code="sleep_duration"`
  - `ActiveCaloriesBurnedRecord` → `metric_code="active_calories"`
  - `BloodPressureRecord` → `metric_code="systolic_bp"` / `"diastolic_bp"`

```kotlin
// Health Connect API Initialization & Availability Check
val sdkStatus = HealthConnectClient.getSdkStatus(context)
if (sdkStatus == HealthConnectClient.SDK_AVAILABLE) {
    val client = HealthConnectClient.getOrCreate(context)
    
    // Incremental Delta Harvesting via Changes Token
    val changesToken = client.getChangesToken(
        ChangesTokenRequest(setOf(StepsRecord::class, HeartRateRecord::class, SleepSessionRecord::class))
    )
    val changes = client.getChanges(changesToken)
    for (change in changes.upsertedRecords) {
        if (change is StepsRecord) {
            val count = change.count
            val recordId = change.metadata.id
        }
    }
}
```

#### Tier 2: Samsung Health Native SDK (`com.samsung.android.sdk.healthdata`)
- **Package**: `com.samsung.android.sdk.healthdata` (Samsung Partner Developer Privileged Library)
- **Standalone Capability**: Functions as a **100% standalone primary health provider** without requiring Google Health Connect installed.
- **Full Spectrum Sensor & Metric Support**:
  - `HealthConstants.StepCount` → `metric_code="steps"`
  - `HealthConstants.HeartRate` → `metric_code="heart_rate"`
  - `HealthConstants.Sleep` → `metric_code="sleep_duration"`
  - `HealthConstants.BloodPressure` → `metric_code="systolic_bp"` / `"diastolic_bp"`
  - `HealthConstants.BloodGlucose` → `metric_code="blood_glucose"`
  - `HealthConstants.OxygenSaturation` → `metric_code="spo2"`
  - `HealthConstants.BodyTemperature` → `metric_code="body_temperature"`
  - `HealthConstants.BodyComposition` → `metric_code="body_fat_pct"`, `"skeletal_muscle_mass"`, `"body_water"`
  - `HealthConstants.WaterIntake` → `metric_code="water"`
  - `HealthConstants.Exercise` → Workout session logs
  - `HealthConstants.Electrocardiogram` → Atrial fibrillation detection data

```kotlin
// Samsung Health SDK Query via HealthDataResolver
val request = HealthDataResolver.ReadRequest.Builder()
    .setDataType(HealthConstants.BodyComposition.HEALTH_DATA_TYPE)
    .setFilter(HealthDataResolver.Filter.greaterThan(HealthConstants.BodyComposition.START_TIME, startTime))
    .build()

val resolver = HealthDataResolver(healthDataStore)
resolver.read(request).setResultListener { result ->
    val iterator = result.iterator
    while (iterator.hasNext()) {
        val data = iterator.next()
        val fatPct = data.getFloat(HealthConstants.BodyComposition.BODY_FAT)           // Körperfett %
        val muscleKg = data.getFloat(HealthConstants.BodyComposition.SKELETAL_MUSCLE)   // Muskelmasse kg
        val uuid = data.getString(HealthConstants.BodyComposition.UUID)                 // Eindeutige ID
    }
}
```
- **Seamless Integration with Salus Source Priority Engine**:
  Salus does **NOT** invent artificial "Single/Dual Provider Modes". In accordance with **DRY** and **SOLID** principles, all native sync plugins operate uniformly by emitting measurements tagged with their respective `source` (e.g. `source="samsung_health"` or `source="health_connect"`).
  
  The **existing Salus Source Priority Engine** (`user_metric_preference.source_priority`) handles 100% of resolution, filtering, and visualization dynamically per metric:
  
  ```
  Salus Existing Source Priority Engine (/settings/sources):
  ┌─────────────────────────────────────────────────────────────┐
  │ metric_code: "steps"                                        │
  │   source_priority: ["samsung_health", "health_connect", ...]│
  ├─────────────────────────────────────────────────────────────┤
  │ metric_code: "body_fat_pct"                                 │
  │   source_priority: ["samsung_health", "manual"]             │
  └─────────────────────────────────────────────────────────────┘
  ```

---

### B. Security, Storage & Biometrics

- **Biometric App Lock (`@capacitor/biometrics`)**: Fingerprint / Face Unlock prompt when opening Salus.
- **Hardware-Backed KeyStore Security**: JWT tokens and asymmetric encryption keys stored in Android `EncryptedSharedPreferences` backed by the hardware TEE (Trusted Execution Environment) or StrongBox.

---

### C. Background Execution & Push Notifications

- **Android `WorkManager`**: Reliable background polling of Health Connect metrics even when the Salus app is closed or the device reboots.
- **Local Notifications (`@capacitor/local-notifications`)**:
  - Medication intake reminders with action buttons ("Take", "Snooze").
  - Rest timer completion alerts during active workout sessions.
  - Circadian light exposure prompts.

---

### D. Haptics & Audio Feedback

- **Haptic Engine (`@capacitor/haptics`)**: Tactile vibration patterns for:
  - Set completion in active workout logger.
  - Rest timer countdown ticks.
  - Habit completion confirmation.

---

## 5. Architectural Decisions & Open Questions

Before proceeding with implementation, the following architectural decisions must be formally aligned:

### Decision 1: Health Sync Strategy — Direct Ingestion vs. Bridge Middleware
- **Option A**: Capacitor Java plugin directly inserts records into Dexie IndexedDB via JavaScript injection.
- **Option B**: Native Android service writes directly to FastAPI REST API (`/api/v1/sync/push`).
- **Recommendation**: **Option A**. Ingesting via the frontend JavaScript bridge ensures all data passes through the client-side `mutate()` gateway, preserving outbox Temporal ordering, conflict detection, and optimistic UI updates.

### Decision 2: OTA (Over-The-Air) Asset Updates
- **Option A**: Build standard APK/AAB binaries; user updates app via Play Store / APK download.
- **Option B**: Integrate CapGo / Live Updates to update HTML/JS/CSS assets without APK re-installation.
- **Recommendation**: Start with **Option A** for complete security and simplicity. Introduce CapGo in Phase 3 if rapid frontend iteration is required.

### Decision 3: Background Polling Frequency & Battery Impact
- **Question**: How often should background `WorkManager` poll Health Connect / Samsung Health?
- **Proposal**: 
  - Periodic background sync every **15 minutes** (Android `WorkManager` minimum interval).
  - Immediate sync when app comes to foreground (`onResume`).
  - Battery optimization: Doze mode compliant using `ExistingPeriodicWorkPolicy.KEEP`.

### Decision 4: Samsung Health SDK Partner Approval
- **Question**: Samsung Health SDK requires developer partner registration for commercial BIA/ECG sensor access.
- **Proposal**: Implement Health Connect as the default primary provider first, with Samsung Health SDK behind a feature flag for developer builds until partner keys are issued.

---

## 6. Implementation Roadmap & Toolchain Setup

### Phase 1: Environment & Tooling (Nix Flake Extension)
Extend `flake.nix` with Android build dependencies:
```nix
pkgs.androidenv.composeAndroidPackages {
  buildToolsVersions = [ "34.0.0" ];
  platformVersions = [ "34" ];
  abiVersions = [ "x86_64" "arm64-v8a" ];
}
```

### Phase 2: Capacitor Integration & Project Initialization
```bash
cd frontend
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init Salus design.fleischer.salus --web-dir build
npx cap add android
```

### Phase 3: Native Health Plugin Development (`android/app/src/main/java/design/fleischer/salus/plugins/`)
- Write `HealthConnectPlugin.java` wrapping `HealthConnectClient`.
- Implement background `HealthSyncWorker.java`.

### Phase 4: Build Automation (`justfile`)
Add just recipes for build, sync, and packaging:
```just
@build-apk:
    just build-frontend
    cd frontend && npx cap sync android
    cd frontend/android && ./gradlew assembleRelease
```

---

## 8. Sensor Mapping Specification & Source Deduplication Protocol

### A. Metric Translation Table

Salus utilizes global, code-defined `MetricDefinition` entries (`metric_code`). Native Android sensor records map directly to these existing definitions:

| Native Sensor Source | Native Record Type | Target Salus `metric_code` | Unit | Conversion Logic |
|---|---|---|---|---|
| Health Connect | `StepsRecord` | `steps` | count | Sum of steps in time window |
| Health Connect | `HeartRateRecord` | `heart_rate` | bpm | Average BPM during sample window |
| Health Connect | `HeartRateVariabilityRmssdRecord` | `hrv` | ms | RMSSD value in milliseconds |
| Health Connect | `SleepSessionRecord` | `sleep_duration` | hours | Duration between `startTime` and `endTime` in hours |
| Health Connect | `BloodPressureRecord` | `systolic_bp` / `diastolic_bp` | mmHg | Systolic and Diastolic values extracted |
| Samsung Health SDK | `com.samsung.health.body_composition` | `body_fat_pct` | % | Bioelectrical Impedance Analysis (BIA) % |
| Samsung Health SDK | `com.samsung.health.body_composition` | `skeletal_muscle_mass` | kg | Muscle mass in kilograms |
| Samsung Health SDK | `com.samsung.health.blood_pressure` | `systolic_bp` / `diastolic_bp` | mmHg | Continuous optical sensor reading |

---

### B. Source Attribution & Deduplication Algorithm

When multi-sensor wearables are connected (e.g. Samsung Galaxy Watch + Oura Ring via Health Connect), Salus applies a two-step deduplication & prioritization pipeline:

```
[Native Sensor Ingestion Event]
               │
               ▼
[Step 1: Idempotency Check via external_id]
   ├── Exists in Dexie/Database? ──► [DISCARD DUPLICATE]
   └── New External Record?       ──► [PROCEED TO STEP 2]
               │
               ▼
[Step 2: Source Priority Resolution]
   ├── Query user_metric_preference for metric_code
   ├── Apply configured Source Priority (e.g. samsung_health > health_connect > manual)
   └── Ingest via mutate({ kind: 'crud', op: 'create', entity: 'measurement', ... })
```

#### Idempotency Key Format:
- Health Connect: `external_id = "health_connect:" + record.metadata.id`
- Samsung Health: `external_id = "samsung_health:" + data.getString(HealthConstants.SessionMeasurement.UUID)`

---

### C. TypeScript Bridge Interface (DIP Contract)

To maintain strict adherence to Dependency Inversion, the frontend interacts exclusively via the `INativeHealthBridge` protocol:

```typescript
export interface IngestedMetricPayload {
  metric_code: string;
  value: number;
  timestamp: string;
  source: 'health_connect' | 'samsung_health' | 'manual';
  source_data_type: string;
  external_id: string;
}

export interface INativeHealthBridge {
  isAvailable(): Promise<boolean>;
  checkPermissions(): Promise<{ granted: boolean; missing: string[] }>;
  requestPermissions(): Promise<boolean>;
  fetchDelta(sinceIso: string): Promise<IngestedMetricPayload[]>;
}
```

- **Browser Implementation (`BrowserHealthBridge`)**: Returns `isAvailable() = false`.
- **Capacitor APK Implementation (`CapacitorHealthBridge`)**: Delegates calls to `Capacitor.Plugins.HealthConnectPlugin` and `Capacitor.Plugins.SamsungHealthPlugin`.

---

## 9. Approved Architecture Decisions Summary

1. **Bridge Ingestion Path**: Approved Ingestion via JS Bridge (`mutate()` gateway -> Dexie IndexedDB -> Standard Outbox Sync to FastAPI).
2. **Multi-SDK Support**: Simultaneous support for Google Health Connect API, Samsung Health SDK (BIA/ECG), Biometrics (Fingerprint/Face Unlock), and KeyStore hardware encryption.
3. **Distribution Target**: Direct APK Sideloading & GitHub Releases for 100% user privacy, zero Play Store dependency, and free distribution.

---

## 10. Unified Notification Architecture & WorkManager Edge Cases

### A. DRY Unified Notification Architecture (PWA & Native APK)

To prevent code duplication, notification scheduling uses a single TypeScript `INotificationProvider` interface:

```typescript
export interface LocalNotificationPayload {
  id: number;
  title: string;
  body: string;
  scheduleAt?: Date;
  actionButtons?: Array<{ id: string; title: string }>;
  extraData?: Record<string, unknown>;
}

export interface INotificationProvider {
  requestPermissions(): Promise<boolean>;
  schedule(payload: LocalNotificationPayload): Promise<void>;
  cancel(id: number): Promise<void>;
}
```

- **PWA Web Provider (`WebNotificationProvider`)**: Uses native browser `Notification` API + Service Worker (`self.registration.showNotification()`).
- **Native APK Provider (`CapacitorNotificationProvider`)**: Uses `@capacitor/local-notifications`. Leverages Android Notification Drawer Action Buttons (e.g. Medication Reminder: `[Take Now]`, `[Snooze 15m]`).
  - Action Click Event: An Android `BroadcastReceiver` intercepts action button clicks in the background and calls `mutate({ kind: 'crud', op: 'create', entity: 'medication_log', ... })` without requiring the app UI to open.

---

### B. External Wearable Workout Session Import

When a user completes an exercise session on a wearable device (e.g. Galaxy Watch, Mi Band, Garmin):
1. **Raw Sensor Data**: Continuous heart rate samples and active calories write to `Measurement` rows (`metric_code="heart_rate"`, `"active_calories"`).
2. **Workout Session Entity**: The native SDK workout log is mapped to a Salus `WorkoutSession` with `source="samsung_health"` or `source="health_connect"`, allowing dashboard & analytics integration.

---

### C. Circadian Sensor-Fusion Integration

Sleep onset, wake times, and light sensor exposure harvested from wearables automatically update the `CircadianProfile` analytics engine. Optimal morning daylight exposure windows, cortisol awakening response, and sleep pressure are recalculated without requiring manual user logging.

---

### D. Android WorkManager Edge Cases & Constraints

The native `HealthSyncWorker.kt` implements robust edge-case handling:

1. **Device Reboot (`BOOT_COMPLETED`)**: Android `WorkManager` automatically reschedules the periodic 15-minute sync worker upon system boot.
2. **Battery Saver & Doze Mode**: Configured with strict Android execution constraints:
   ```kotlin
   val constraints = Constraints.Builder()
       .setRequiresBatteryNotLow(true)
       .setRequiresStorageNotLow(true)
       .build()
   ```
3. **Offline Queueing**: If the device is offline during a background sync, harvested metrics are stored locally in Android `EncryptedSharedPreferences` / Dexie. They queue automatically in the Salus Outbox until network connectivity is restored.

---

## 11. Android Home Screen Widgets, Quick Settings Tiles & Deep Linking

### A. Android Home Screen Widgets (`AppWidgetProvider`)

Salus native APK integrates custom Android Glance / App Widgets for the Android Home Screen:

1. **Daily Metrics Progress Ring Widget**:
   - Displays real-time step count, water intake progress, and upcoming medication reminders.
   - Reads directly from local Dexie / SQLite data via background worker.
2. **Quick Action Shortcuts Widget**:
   - `[+250ml Water]` — Instantly logs 250ml water intake.
   - `[Start Workout]` — Opens `/workouts/active` directly.

---

### B. Quick Settings Tile (`TileService`)

Salus registers an Android Quick Settings Tile in the notification shade:
- **"Log Water" Tile**: Single-tap in Android Quick Settings shade to log water without launching the full app UI.
- **"Active Workout" Tile**: Single-tap to toggle active workout session drawer.

---

### C. Deep Linking & Protocol Handlers (`salus://`)

Salus registers custom URL schemes and App Links in `AndroidManifest.xml`:
- Scheme: `salus://`
- Host: `salus.fleischer.design`

#### Deep Link Routing Table:
- `salus://workouts/active` ➔ Directly loads Active Workout View
- `salus://entries/[metric_code]` ➔ Directly loads Metric Detail View
- `salus://medications` ➔ Directly opens Medication Tracker
- `salus://sharing/webfinger` ➔ Handles federation and E2EE sharing links

---

## 12. Security, Sandboxing & File-Based Encryption (FBE)

Health data security is enforced at both the Android OS and application layers:

1. **Android UID Sandboxing**: Android assigns a unique Linux User ID (UID) to the Salus APK. The WebView storage directory (`/data/data/design.fleischer.salus/app_webview/`) is accessible strictly by the Salus process.
2. **File-Based Encryption (FBE)**: Salus leverages Android Direct Boot and File-Based Encryption. Local IndexedDB databases are encrypted using device-level keys derived when the device is unlocked.
3. **Hardware TEE KeyStore**: Session JWT tokens, biometric encryption keys, and asymmetric E2EE share keys are stored in the Android Hardware KeyStore (TEE / StrongBox backed).
4. **Biometric Guard**: Native `@capacitor/biometrics` prompt enforces biometric authentication (Fingerprint / Face Unlock) upon app resume or cold boot.

---

## 13. Reproducible Nix CI/CD Build Automation

Salus mandates reproducible, headless APK builds via Nix Flake integration:

### A. Nix Environment Integration (`flake.nix`)
```nix
pkgs.androidenv.composeAndroidPackages {
  buildToolsVersions = [ "34.0.0" ];
  platformVersions = [ "34" ];
  abiVersions = [ "x86_64" "arm64-v8a" ];
  includeNDK = false;
}
```

### B. Just Recipe Automation (`justfile`)
```just
# Build production release APK
@build-apk:
    just build-frontend
    cd frontend && npx cap sync android
    cd frontend/android && ./gradlew assembleRelease
    @echo "APK successfully built: frontend/android/app/build/outputs/apk/release/app-release-unsigned.apk"
```

---

## 14. Device Management Subsystem Integration & Native Export

### A. Integration with Salus `device` Model & Remote De-authorization

Salus possesses a formal Device Management Subsystem (`docs/device-management.md`). The Native APK integrates directly with this framework:

1. **Automatic Device Registration**: Upon native app initialization, `@capacitor/device` retrieves:
   - Hardware Model (e.g. `Samsung SM-S918B / Galaxy S23 Ultra`)
   - Battery Level & Battery Charging Status (`battery_level`)
   - Operating System & Firmware Version (`firmware_version`)
2. **Device State Telemetry**: Automatically creates/updates a `Device` record in Salus DB (`device_type_code="android_smartphone"` or `"galaxy_watch"`), maintaining `last_seen_at` and `battery_level` telemetry in the background.
3. **Web UI Remote De-authorization**:
   - In `/settings/devices`, users can view all active native devices and click **[Deauthorize Device]**.
   - Remote revocation invalidates the device's associated API token/session key in the backend.
   - Upon the next background sync attempt, the APK receives a `401 Unauthorized` status, wipes its hardware KeyStore session token, and displays a secure re-authentication prompt.

---

### B. Native Dual-Mode File Exports (Offline Dexie + Backend Streaming)

Salus features CSV/JSON export and health PDF report generation (`docs/pdf-reports.md`, `src/salus/routers/export.py`):

1. **Online Mode (Backend Streaming)**:
   - Calls `/api/v1/export/download?format=csv|json` to retrieve full server-side historical exports.
2. **100% Offline Mode (Local Dexie Export)**:
   - When offline, the SvelteKit SPA reads directly from Dexie IndexedDB (`db.measurement`, `db.workout_session`, `db.medication_log`), serializes the data to CSV/JSON in memory, and uses `@capacitor/filesystem` to save the file into the Android `Downloads` directory.
3. **Android Share Sheet Integration**:
   - Downloaded CSV/JSON/PDF files trigger `@capacitor/share`, opening the native Android share sheet for instant sharing via email or messaging apps.

---

## 15. Directory & Project Structure

The project layout follows strict **SOLID** and **DRY** scoping:

```
salus/
├── src/salus/                          ← FastAPI Backend Service
├── docs/
│   └── native-apk-bundling.md          ← Master Architectural Specification
└── frontend/                           ← SvelteKit SPA + Capacitor Frontend
    ├── android/                        ← Native Android Studio / Gradle Project
    │   └── app/src/main/
    │       ├── java/design/fleischer/salus/
    │       │   ├── MainActivity.java
    │       │   └── plugins/
    │       │       ├── HealthConnectPlugin.kt      <-- Google Health Connect SDK
    │       │       ├── SamsungHealthPlugin.kt      <-- Samsung Health Privileged SDK
    │       │       ├── BiometricAuthPlugin.kt      <-- KeyStore & Biometrics
    │       │       └── HealthSyncWorker.kt         <-- Background WorkManager Job
    │       └── AndroidManifest.xml
    └── src/
        └── lib/
            └── native/                 ← TypeScript Native Bridge Layer (DIP)
                ├── bridge.ts           ← Factory (Browser vs. Capacitor Detector)
                ├── types.ts            ← Protocol Interfaces (INativeHealthBridge, etc.)
                └── providers/
                    ├── browser-health.ts     ← Web Browser Fallback (No-Op)
                    ├── capacitor-health.ts   ← Capacitor Native SDK Invoker
                    ├── browser-notify.ts     ← Web Notification API
                    └── capacitor-notify.ts   ← Local Notifications + Action Drawer
```

---

## 16. Sources View Integration & Native Controls (`/settings/sources`)

The existing Quellen-Ansicht (`frontend/src/routes/settings/sources/+page.svelte`) is already designed for multi-source management. Native APK capabilities enhance this view seamlessly:

1. **Automatic Measurement Counter & Source Card Activation**:
   - `KNOWN_SOURCES` already defines `health_connect` (`#3ddc84`) and `samsung_health` (`#1428a0`).
   - The moment native background sync ingests data, `liveQuery()` automatically updates total measurement counts and activates the source cards without UI changes.
2. **Native Permission & Sync Controls**:
   - **In Browser Mode**: Displays informative badge ("Requires Native Android APK").
   - **In Native APK Mode**: Shows direct interactive controls inside the source detail modal (`SourceDetailsModal.svelte`):
     - **[Grant Android Permissions]**: Triggers `CapacitorHealthBridge.requestPermissions()`.
     - **[Sync Now]**: Manually triggers an immediate delta harvesting run (`fetchDelta()`).
     - **Telemetry Status**: Displays `Last Synced: 2 mins ago` and native SDK connection health.
3. **Per-Metric Priority Drag-and-Drop**:
   - Users can drag `samsung_health` above `health_connect` or `manual` per individual metric card (via `SourcePriorityCard.svelte`), persisting custom rankings to `user_source_preference`.







