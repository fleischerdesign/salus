# Salus 2.0 — Detaillierte Unterseiten- & Routen-Architektur (Alle 31 Routen)
**Dokument:** `15-subpages-and-route-architecture.md`  
**Status:** Verbindlich  
**Zweck:** Lückenlose Spezifikation aller 31 Unterseiten, View-States, Sub-Modals und Workflows in Salus 2.0.

---

## 1. Übersicht der 31 Routen nach den 4 Säulen

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DIE 31 SALUS 2.0 ROUTEN IM DETAIL                                    │
├───────────────────┬──────────────────────────────────┬─────────────────────────────────────────────────┤
│ Säule             │ Pfad (URL)                       │ Zweck & View-States                             │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────────────────────┤
│ **1. HEUTE**      │ `/`                              │ Modulares Dashboard Cockpit (Edit Mode, Drawer) │
│                   │ `/onboarding`                    │ 4-Stufen Initialisierungs-Wizard                │
│                   │ `/notifications`                 │ Benachrichtigungs- & Zirkadian-Mitteilungen     │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────────────────────┤
│ **2. TRACK**      │ `/entries`                       │ Übersicht aller Metrik-Karten & Gruppen         │
│                   │ `/entries/[id]`                  │ Dual-View: Metrik-Detail oder Gruppenansicht    │
│                   │ `/entries/[id]/[metric_code]`    │ Metrik-Detail innerhalb einer Gruppe (z.B. RR)  │
│                   │ `/workouts`                      │ Workout-Hub: Split-Übersicht & Historie         │
│                   │ `/workouts/active`               │ Live-Training Focus Screen (Sticky, RestTimer)  │
│                   │ `/workouts/plans`                │ Trainingsplan-Verwaltung & Split-Editor         │
│                   │ `/workouts/plans/[id]/edit`      │ Drag-and-Drop Split- & Übungs-Editor            │
│                   │ `/workouts/exercises`            │ Übungs-Bibliothek mit 1RM-Kurven & Muskel-Filter│
│                   │ `/food`                          │ Tägliches Ernährungstagebuch mit Makro-Donut   │
│                   │ `/food/custom`                   │ Eigene Lebensmittel anlegen (Nährwertrechner)   │
│                   │ `/recipes`                       │ Rezept-Katalog & Meal-Prep-Zentrale             │
│                   │ `/recipes/[id]`                  │ Rezept-Detail & dynamischer Portionsskalierer   │
│                   │ `/fasting`                       │ Fasten-Tracker mit Stoffwechsel-Zonen           │
│                   │ `/habits`                        │ Habit-Dashboard mit 365-Tage Matrix             │
│                   │ `/journal`                       │ Zen-Modus Reflexions-Tagebuch mit Markdown      │
│                   │ `/mood`                          │ 2D-Valenz/Arousal Stimmungs-Tracker             │
│                   │ `/labs`                          │ Labor-Panel-Übersicht & Leitlinien-Tachos       │
│                   │ `/labs/[panel_id]`               │ Panel-Detail & Multi-Draw Zeitreihen-Tabelle    │
│                   │ `/medications`                   │ Medikationsplan, Adhärenz (PDC) & Vorrat        │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────────────────────┤
│ **3. INSIGHTS**   │ `/analytics`                     │ Korrelations-Matrix, Trends & Datenanalyse      │
│                   │ `/coach`                         │ Zirkadianer Tages-Coach & KI/Regel-Empfehlungen │
│                   │ `/coach/circadian`               │ 24h-Sonnenbogen & Chronotyp-Analyse             │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────────────────────┤
│ **4. HUB**        │ `/goals`                         │ Ziel-Zentrale mit Fortschrittskorridoren        │
│                   │ `/goals/new`                     │ Mathematischer Ziel-Erstellungs-Wizard          │
│                   │ `/community`                     │ Anonymisierte Challenges & Ranglisten           │
│                   │ `/achievements`                  │ 3D-Tilt Trophäen & Meilensteine                 │
│                   │ `/settings`                      │ Haupt-Einstellungen (Profil, Theme, Einheiten)  │
│                   │ `/settings/shares`               │ E2EE Arzt-Freigaben & PIN-Management            │
│                   │ `/settings/export`               │ CSV, JSON, Apple Health XML Export/Import       │
│                   │ `/settings/security`             │ API-Tokens, Passwörter, OIDC & LDAP-Bind        │
│                   │ `/admin`                         │ System-Administration, DB-Status & Benutzer     │
└───────────────────┴──────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 2. Detail-Spezifikation kritischer Sub-Routen

### 2.1 `/workouts/plans/[id]/edit` — Der Drag-and-Drop Split-Editor
- **Zweck:** Erstellen und Umordnen von Übungen innerhalb eines Workout-Splits.
- **Interaktion:**
  - Jede Übungszeile besitzt einen Drag-Handle `[ ⠿ ]`. Durch Ziehen wird die Reihenfolge in Echtzeit neu angeordnet (`HTML5 Drag and Drop` / `svelte-dnd-action`).
  - Direkte Konfiguration von Zielsätzen (z. B. `3 Sätze`), Wiederholungsbereich (`8–10 Wdh.`) und Pausenzeit (`90s RestTimer`).
  - Live-Aktualisierung des Ziel-Volumens in `MuscleHeatmap2D.svelte` in der rechten Seitenleiste.

### 2.2 `/settings/shares` — E2EE Arzt- & Therapeuten-Freigabe
- **Zweck:** Zeitlich begrenzte, kryptographisch gesicherte Freigaben für medizinisches Personal.
- **Workflow:**
  1. Klick auf `[ + Neue Freigabe erstellen ]` öffnet `Stepper.svelte`.
  2. **Schritt 1:** Datenumfang wählen (z.B. `[✓] Blutdruck`, `[✓] Lipidprofil`, `[ ] Journal ausschließen`).
  3. **Schritt 2:** Gültigkeit definieren (`24 Stunden`, `7 Tage`, `Einmaliger Abruf`) und optionale 6-stellige PIN (`OtpInput.svelte`) vergeben.
  4. **Schritt 3:** Das System generiert einen clientseitig asymmetrisch verschlüsselten Link (`https://salus.app/s/xyz#key=...`).
  5. **Audit-Log:** Anzeige aller bisherigen Zugriffe (Datum, abgerufene Datenmenge, IP-Hash).

### 2.3 `/admin` — System- & Benutzer-Verwaltung
- **Zweck:** Administrationszentrale für Self-Hosted Instanzen.
- **Elemente:**
  - **Server-Health:** Datenbankgröße (`salus.db`), SQLite WAL-Status, Server-Latenz, SSE Live-Sync Verbindungen.
  - **Benutzerverwaltung:** Tabelle (`DataTable.svelte`) mit Benutzerrollen (Admin / User), Speicherplatzverbrauch, letzter Synchronisation und Deaktivierungs-Option.
  - **Audit-Log:** Live-Feed aller Autorisierungs-Events und fehlgeschlagener Login-Versuche.

### 2.4 `/onboarding` — 4-Stufen Initialisierungs-Wizard
- **Stufe 1 (Biometrie):** Geburtsjahr, Geschlecht, Primäre Einheiten (Metrisch kg/cm vs. Imperial lbs/inch, Blutzucker mg/dL vs. mmol/L).
- **Stufe 2 (Fokus-Bereiche):** Auswahl der relevanten Kacheln (z. B. *„Kardiologische Gesundheit & Blutdruck“*, *„Muskelaufbau & Kraftsport“*, *„Stoffwechsel & Fasten“*).
- **Stufe 3 (Zirkadian-Kalibrierung):** Typische Aufwach- und Schlafenszeit zur Initialisierung des Sonnenbogens (`CircadianSunArc`).
- **Stufe 4 (Daten-Import):** Optionaler 1-Klick Import von Apple Health XML oder Vorwochen-CSV via `FileUpload.svelte`.
