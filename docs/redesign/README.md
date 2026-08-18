# Salus 2.0 — Redesign Dokumentations-Zentrale

Willkommen in der modularen Spezifikations-Dokumentation für das **Salus 2.0 UI/UX-Redesign**.

Dieses Verzeichnis dient als zentrale Wissensbasis für die ganzheitliche visuelle, funktionale und interaktive Transformation von Salus von einem nüchternen Datenbank-Dashboard zu einem eleganten, motivierenden und wissenschaftlich exakten **Personal Health Companion**.

---

## 📑 Struktur der Spezifikationen

| Datei | Thema & Inhalt |
|---|---|
| [**`01-design-system.md`**](./01-design-system.md) | OKLCH-Farbräume, Surface-Elevationen, Typografie-Hierarchie, Abstände, Schatten, Radien, Barrierefreiheit & Farbfehlsichtigkeits-Modi. |
| [**`02-information-architecture.md`**](./02-information-architecture.md) | Das 4-Säulen-Modell, Routing-Baum, Desktop-Shell, Mobile PWA-Shell, Bottom-Navigation & Tastatur-Shortcuts (`Cmd+K`). |
| [**`03-quick-log-system.md`**](./03-quick-log-system.md) | Der universelle Schnellerfassungs-Hub (FAB / Taste `L`), 1-Tap Wasser-, Stimmungs- und Habit-Logging, Ziffernblock-Erfassung. |
| [**`04-visual-delight-engine.md`**](./04-visual-delight-engine.md) | Animierte Vektorgrafiken & SVG-Metaphern (Wellen-Wasserglas, Stoffwechsel-Uhr, Muskel-Heatmap, Schlaf-Hypnogramm, Tachos, Live-Galerie). |
| [**`05-user-journey-flows.md`**](./05-user-journey-flows.md) | Die 5 lückenlosen Tagesabläufe (Morgen-Routine, Workout Focus Mode, Mittags-Ernährung, Abend-Wind-down, Arzt-Export). |
| [**`06-domains-deep-dive.md`**](./06-domains-deep-dive.md) | Tiefenspezifikation aller Domänen: Dashboard-Widget-Engine, Metriken, Workouts, Food, Fasten, Habits, Labore, Medikamente, Mental, Goals & Sharing. |
| [**`07-component-library.md`**](./07-component-library.md) | Vollständiger Komponenten-Katalog (Atome, Moleküle, Organismen), Props, Zustände, Haptik & Barrierefreiheit. |
| [**`08-charts-and-data-viz.md`**](./08-charts-and-data-viz.md) | Standards für Datenvisualisierung: Zeitachsen, 7-Tage-EMAs, Konfidenzintervalle, Tooltip-Scrubbing & Zielkorridore. |
| [**`09-system-states-and-edge-cases.md`**](./09-system-states-and-edge-cases.md) | Offline-Betrieb (Dexie-Outbox), Konflikt-Handling, Shimmer-Skeletons, Session-Ablauf, Plausibilitätswarnungen. |
| [**`10-implementation-roadmap.md`**](./10-implementation-roadmap.md) | 4-Phasen-Migrationsplan mit Abhängigkeits-Matrix und Zero-Regression-Garantie. |
| [**`11-clinical-and-scientific-standards.md`**](./11-clinical-and-scientific-standards.md) | Standards für Ärzte, Ernährungsberater & Wissenschaftler (Dual-Layer UI, SI-Einheiten, Referenz-Tachos, Ratios, PDC-Adhärenz, Arztbrief-PDF). |
| [**`12-screen-wireframes-and-layouts.md`**](./12-screen-wireframes-and-layouts.md) | Exakte 12-Spalten-Raster & visuelle ASCII-Wireframes für Desktop, Tablet & Smartphone (Dashboard, Workout, Food, Labs). |
| [**`13-css-tokens-and-theme.md`**](./13-css-tokens-and-theme.md) | Vollständige `app.css` Token-Definition (OKLCH, Surface-Elevationen, Radien, Animationen). |
| [**`14-motion-and-gestures.md`**](./14-motion-and-gestures.md) | Svelte-5 Spring-Physik, Schwellenwerte für Touch-Gesten, Haptik-Impulsmuster & Web Audio Synthesizer. |
| [**`15-subpages-and-route-architecture.md`**](./15-subpages-and-route-architecture.md) | Spezifikation aller 31 Unterseiten, View-States & Sub-Workflows (Admin, Split-Editor, E2EE Shares, Onboarding). |
| [**`16-form-validation-and-plausibility-engine.md`**](./16-form-validation-and-plausibility-engine.md) | Mathematische & klinische Plausibilitätsgrenzen (~40 Metriken), Ausreißer-Flags & Zahlen-Parsing (Komma vs. Punkt). |
| [**`17-dexie-schema-and-indexing-strategy.md`**](./17-dexie-schema-and-indexing-strategy.md) | IndexedDB (Dexie.js) Compound-Indexe, Reaktivität via `useQuery` & migrationssichere Schema-Versionen. |
| [**`18-offline-sync-and-concurrency-matrix.md`**](./18-offline-sync-and-concurrency-matrix.md) | Crash-Resistenz aktiver Workouts, State-Wiederherstellung nach Browser-Reload & SSE Exponential Backoff. |
| [**`19-accessibility-and-colorblind-engine.md`**](./19-accessibility-and-colorblind-engine.md) | WCAG 2.2 AAA, OKLCH-Farbanpassungen für Protanopie/Deuteranopie/Tritanopie & `prefers-reduced-motion`. |
| [**`20-power-user-shortcuts-and-command-engine.md`**](./20-power-user-shortcuts-and-command-engine.md) | Vollständige `Cmd+K` Command-Palette Registry, Einzel-Tasten-Navigation (`L`, `W`, `J`, `K`, `X`, `E`) & Shortcuts. |
| [**`21-security-and-cryptographic-architecture.md`**](./21-security-and-cryptographic-architecture.md) | Zero-Knowledge E2EE Arzt-Freigaben (WebCrypto AES-GCM 256, PBKDF2), CSP & API-Token Scopes. |
| [**`22-internationalization-and-localization.md`**](./22-internationalization-and-localization.md) | Typsichere Mehrsprachigkeit (de-DE, en-US, fr-FR), native `Intl` Formatierung & medizinisches Fachwörterbuch. |
| [**`23-push-notifications-and-background-sync.md`**](./23-push-notifications-and-background-sync.md) | Web Push API (VAPID), Service Worker Push-Actions (1-Tap Logging) & zirkadianes Notification-Scheduling. |
| [**`24-testing-and-quality-assurance-strategy.md`**](./24-testing-and-quality-assurance-strategy.md) | Test-Pyramide, mathematische Formel-Tests (r, rho, 1RM, EMA), Vitest & Playwright E2E / Visual Regression. |
| [**`25-performance-budgets-and-optimization.md`**](./25-performance-budgets-and-optimization.md) | Core Web Vitals (INP < 50ms, CLS = 0.00, LCP < 1.2s), dynamisches Code-Splitting & Listen-Virtualisierung. |
| [**`26-data-migration-and-legacy-compatibility.md`**](./26-data-migration-and-legacy-compatibility.md) | Zero-Data-Loss Migration bestehender SQLite/Postgres-Datenbanken & automatisches Dexie Client-Upgrade (v1 -> v15). |

---

## 🎯 Leitbild: *Academic Precision meets Sensory Delight*
Jede Komponente, jede Interaktion und jede Dokumentationsdatei in diesem Verzeichnis folgt den 6 Grundsätzen:
1. **Zero Logging Friction** (Erfassung unter 2 Sekunden).
2. **Der Tag als biologisches Kontinuum** (Zirkadianer Fluss).
3. **Glanceable UI & Progressive Disclosure** (Sofort-Orientierung + Tiefe bei Bedarf).
4. **Mobile-First & PWA-Daumen-Ergonomie** (Bottom Sheets statt zentrierter Modals).
5. **Visuelle Ruhe durch strenge Tokenisierung** (Kein Tabellen-Chaos).
6. **Wissenschaftliche Transparenz & Local-First Datenhoheit**.
