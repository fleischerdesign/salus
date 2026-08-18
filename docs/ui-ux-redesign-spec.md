# Salus 2.0 — Vollständige Master-Spezifikation für UI/UX & Design-System
**Dokument-Version:** 2.1.0  
**Status:** Verbindliche Architektur- und Design-Planung  
**Fokus:** Lückenlose Spezifikation aller Screens, Interaktionen, Komponenten, Zustände und Datenflüsse.

---

## Inhaltsverzeichnis

1. [Strategische Vision & Design-Prinzipien](#1-strategische-vision--design-prinzipien)
2. [Design-System & Token-Architektur](#2-design-system--token-architektur)
   - 2.1 Farbraum & Semantik (OKLCH)
   - 2.2 Oberflächen- & Tiefen-Hierarchie (Surfaces & Elevation)
   - 2.3 Typografie-Maßstab & Tabellarische Zahlen
   - 2.4 Spacing-, Radius- & Animations-Tokens
   - 2.5 Barrierefreiheit, Kontraste & Farbfehlsichtigkeit
3. [Informationsarchitektur & Routing-Struktur](#3-informationsarchitektur--routing-struktur)
   - 3.1 Die 4 Säulen & URL-Mapping
   - 3.2 Responsive Shell (Desktop vs. Tablet vs. PWA Mobile)
   - 3.3 Tastatur-Steuerung & Command Palette (`Cmd+K`)
4. [Der Universal Quick-Log Hub (Zero-Friction Capture)](#4-der-universal-quick-log-hub-zero-friction-capture)
5. [Detaillierte Screen-by-Screen-Spezifikation](#5-detaillierte-screen-by-screen-spezifikation)
   - 5.1 Säule 1: **Heute / Dashboard** (`/`) — Das voll-anpassbare Cockpit
   - 5.2 Säule 2: **Track & Body** (`/track/*`)
     - 5.2.1 Metriken- & Vitalwerte-Logbuch (`/track/metrics`)
     - 5.2.2 Workouts & Krafttraining (`/track/workouts/*`)
     - 5.2.3 Ernährung & Food-Datenbank (`/track/nutrition/*`)
     - 5.2.4 Fasten-Tracker (`/track/fasting`)
     - 5.2.5 Gewohnheiten (Habits & Streaks) (`/track/habits/*`)
     - 5.2.6 Klinische Labordaten (`/track/labs`)
     - 5.2.7 Medikamente & Supplemente (`/track/medications/*`)
     - 5.2.8 Mental Health (Mood & Journal) (`/track/mental/*`)
   - 5.3 Säule 3: **Insights & Intelligence** (`/insights/*`)
     - 5.3.1 Globale Trends & Korrelations-Matrix (`/insights/trends`)
     - 5.3.2 Zirkadianer Coach & Rhythmus-Uhr (`/insights/circadian`)
     - 5.3.3 Forecast Lab (Prognose-Simulator) (`/insights/forecast`)
     - 5.3.4 KI-Gesundheitscoach (Chat) (`/insights/coach`)
     - 5.3.5 Datenqualitäts-Inspektor (`/insights/data-quality`)
   - 5.4 Säule 4: **Hub, Community & Settings** (`/hub/*` & `/settings/*`)
     - 5.4.1 Ziele, Meilensteine & Mathematische Prognosen (`/hub/goals`)
     - 5.4.2 Achievements & Trophäen-System (`/hub/achievements`)
     - 5.4.3 Community, Feed & Leaderboard (`/hub/community/*`)
     - 5.4.4 E2EE-Freigaben & Sharing (`/settings/shares`)
     - 5.4.5 Geräte, Quellen & Datenexport (`/settings/sources`)
     - 5.4.6 Account, Sicherheit & App-Konfiguration (`/settings/app`)
6. [Das Grafische Visualisierungs- & Illustrierte Komponenten-System (*Visual Delight Engine*)](#6-das-grafische-visualisierungs---illustrierte-komponenten-system-visual-delight-engine)
7. [Lückenlose User Journey Flows (End-to-End Flows)](#7-lückenlose-user-journey-flows-end-to-end-flows)
8. [Komponenten-Bibliothek & Datenvisualisierungs-Standards](#8-komponenten-bibliothek--datenvisualisierungs-standards)
9. [Zustands-Management & Edge Cases](#9-zustands-management--edge-cases)
10. [Schrittweiser Migrations- & Implementierungsplan](#10-schrittweiser-migrations---implementierungsplan)
11. [Freigabe & Verbindlichkeit](#11-freigabe--verbindlichkeit)

---

## 1. Strategische Vision & Design-Prinzipien

### 1.1 Das Leitbild: *Academic Precision meets Sensory Delight*
Salus transformiert sich von einem funktionalen, aber nüchternen Datenbank-Dashboard zu einem **hochgradig ästhetischen, wissenschaftlich fundierten und motivierenden täglichen Gesundheitsbegleiter**. 

Die Interaktion mit Gesundheitsdaten darf sich nicht wie das Ausfüllen einer Steuertabelle anfühlen, sondern muss Klarheit, Motivation und unmittelbares Feedback vermitteln – ohne je die akademische Exaktheit der zugrundeliegenden Biologie und Mathematik zu kompromittieren.

### 1.2 Die 6 Grundgesetze des Salus-UX
1. **Erfassung unter 2 Sekunden (Zero Logging Friction):**  
   Tägliche Einträge (Wasser, Gewicht, Stimmung, Mahlzeit, Habit-Häkchen) müssen von jedem beliebigen Screen mit maximal zwei Fingertipps oder Tastatur-Befehlen erfasst sein.
2. **Der Tag als Kontinuum (Chronologische Ganzheit):**  
   Gesundheit ist kein Silo aus getrennten Tabellen. Der Tag wird als biologischer Fluss visualisiert: Zirkadiane Phasen, Mahlzeitenfenster, Trainingszeiten und Schlaf-Vorbereitung greifen ineinander.
3. **Glanceable UI & Progressive Disclosure:**  
   Die oberste Ebene beantwortet in 3 Sekunden die Fragen: *„Wie stehe ich heute da?“* und *„Was ist mein nächster optimaler Schritt?“*. Tiefe statistische Analysen, Rohwert-Tabellen und wissenschaftliche Begründungen sind bei Bedarf mit einem Klick erreichbar, überladen aber niemals den Primärfokus.
4. **PWA- & Daumen-Ergonomie:**  
   Volle Unterstützung für Smartphone-Einhandbedienung. Kritische Aktionen liegen in der unteren Bildschirmhälfte (Bottom Navigation, Bottom Sheets). Desktop-Modals werden auf Mobilgeräten ausnahmslos durch wischbare Bottom Sheets ersetzt.
5. **Visuelle Ruhe durch strenge Tokenisierung:**  
   Verzicht auf willkürliche Borders, Kasten-Verschachtelungen und unruhige Tabellenzeilen. Struktur entsteht durch saubere typografische Hierarchie, sanfte Ton-in-Ton-Flächen und gezielte Akzentfarben.
6. **Wissenschaftliche Transparenz & Datenhoheit:**  
   Jedes Diagramm und jeder Zirkadian-Hinweis visualisiert seine Berechnungsgrundlage (z. B. 7-Tage-EMA, Konfidenzintervalle, Halbwertszeiten). Alle Daten bleiben Local-First in Dexie und synchronisieren verschlüsselt.

---

## 2. Design-System & Token-Architektur

### 2.1 Farbraum & Semantik (OKLCH)

Das Farbsystem basiert vollständig auf dem **OKLCH-Farbraum**, um absolut konsistente Helligkeitsabstufungen (Perceptual Uniformity) über alle Schattierungen und Modi hinweg zu garantieren.

```
┌──────────────────┬─────────────────────────────┬────────────────────────────────────┐
│ Domäne / Token   │ OKLCH-Farbwert (Light/Dark) │ Funktion & Semantik                │
├──────────────────┼─────────────────────────────┼────────────────────────────────────┤
│ --color-primary  │ oklch(0.52 0.19 285)        │ Brand, Fokus, Hauptaktionsbuttons  │
│ --color-vital    │ oklch(0.58 0.22 18)         │ Herz, Blutdruck, Puls, Gefäße      │
│ --color-activity │ oklch(0.62 0.20 48)         │ Workouts, Schritte, Aktivenergie   │
│ --color-circadian│ oklch(0.68 0.16 75)         │ Sonnenlicht, Wachheit, Fokusfenster│
│ --color-hydrate  │ oklch(0.64 0.15 210)        │ Wasseraufnahme, Fasten-Timer       │
│ --color-nutrition│ oklch(0.60 0.17 148)        │ Ernährung, Kalorien, Makronährstoff│
│ --color-sleep    │ oklch(0.54 0.18 295)        │ Schlafzyklen, HRV, Erholung        │
│ --color-mind     │ oklch(0.62 0.14 330)        │ Stimmung, Stress, Journal, Achtsamk│
│ --color-clinical │ oklch(0.58 0.14 185)        │ Laborwerte, Biomarker, Medikamente │
│ --color-success  │ oklch(0.62 0.17 150)        │ Zielerreichung, positive Trends    │
│ --color-warning  │ oklch(0.70 0.15 80)         │ Schlaffehlbetrag, Warnschwellen    │
│ --color-error    │ oklch(0.58 0.21 25)         │ Kritische Laborwerte, Abbruch      │
└──────────────────┴─────────────────────────────┴────────────────────────────────────┘
```

### 2.2 Oberflächen- & Tiefen-Hierarchie (Surfaces & Elevation)

```
Ebene 0 (Hintergrund):    --color-surface-bg      oklch(0.985 0.002 260)  [Dark: oklch(0.13 0.01 260)]
Ebene 1 (Karten/Panel):   --color-surface-card    #ffffff                 [Dark: oklch(0.17 0.01 260)]
Ebene 2 (Innere Kacheln): --color-surface-subtle  oklch(0.965 0.004 260)  [Dark: oklch(0.21 0.01 260)]
Ebene 3 (Hover/Aktiv):    --color-surface-hover   oklch(0.935 0.006 260)  [Dark: oklch(0.26 0.01 260)]
Ebene 4 (Overlays/Sheets):--color-surface-overlay #ffffff (mit Blur)      [Dark: oklch(0.19 0.01 260)]
```

- **Schatten-System:**
  - `shadow-card`: `0 2px 10px -2px oklch(0 0 0 / 0.04), 0 1px 3px -1px oklch(0 0 0 / 0.02)` (Sehr weich, keine harten Kanten).
  - `shadow-float`: `0 12px 32px -4px oklch(0 0 0 / 0.08), 0 4px 12px -2px oklch(0 0 0 / 0.04)` (Für Dropdowns, Sheets & FAB).
  - `shadow-glow-[color]`: Subtiler farbiger Schimmer für aktive Zustände (z. B. laufendes Workout oder erreichte Ziele).

- **Radien-System:**
  - `radius-sm`: `6px` (Badges, Tags, kleine Schalter)
  - `radius-md`: `10px` (Inputs, Buttons, Tab-Pills)
  - `radius-lg`: `16px` (Standard-Karten, Widgets, Innere Container)
  - `radius-xl`: `24px` (Große Hero-Karten, Modals, Bottom Sheets)
  - `radius-full`: `9999px` (Pillen-Buttons, Avatar, Progress-Ringe)

### 2.3 Typografie-Maßstab & Tabellarische Zahlen
- **Primärschrift:** `Manrope` (Humanist Geometric Sans).
- **Zahlen & Daten:** `JetBrains Mono` oder `Manrope` mit `font-variant-numeric: tabular-nums lining-nums`.

```
┌──────────────────────┬─────────┬────────┬───────────────┬───────────────────────────────┐
│ Token                │ Größe   │ Weight │ Tracking      │ Einsatzbereich                │
├──────────────────────┼─────────┼────────┼───────────────┼───────────────────────────────┤
│ text-display         │ 36–44px │ 800    │ -0.03em       │ Haupt-Messwerte (z.B. 8.420)  │
│ text-hero-title      │ 26–30px │ 700    │ -0.02em       │ Begrüßung / Screen-Header     │
│ text-section-title   │ 18–20px │ 600    │ -0.01em       │ Widget-Kopf / Bereichs-Header │
│ text-card-title      │ 14–15px │ 600    │ 0.00em        │ Kacheltitel                   │
│ text-body            │ 14px    │ 400    │ 0.00em        │ Fließtext, Beschreibungen     │
│ text-body-sm         │ 12–13px │ 400    │ +0.01em       │ Metadaten, Zeitstempel        │
│ text-caption         │ 11–12px │ 700    │ +0.06em (UPPER│ Kategorie-Overlines           │
│ text-metric-unit     │ 13–14px │ 600    │ 0.00em        │ Einheiten (bpm, kcal, kg)     │
└──────────────────────┴─────────┴────────┴───────────────┴───────────────────────────────┘
```

### 2.4 Spacing-, Radius- & Animations-Tokens
- **Spacing-Grid:** 4px Basis (`space-1` = 4px, `space-2` = 8px, `space-3` = 12px, `space-4` = 16px, `space-6` = 24px, `space-8` = 32px).
- **Transitions & Micro-Animations:**
  - Fast (Hover, Toggles): `150ms cubic-bezier(0.4, 0, 0.2, 1)`
  - Normal (Accordion, Tab-Switch, Modals): `250ms cubic-bezier(0.16, 1, 0.3, 1)`
  - Sheet / Page Transition: `350ms cubic-bezier(0.32, 0.72, 0, 1)` (Flüssiges Spring/Decay).

### 2.5 Barrierefreiheit & Farbfehlsichtigkeit
- Alle Text-/Hintergrund-Paare erfüllen mindestens **WCAG AA (4.5:1)** Kontrast.
- **Farbfehlsichtigkeits-Modus (`data-colorblind="true"`):**  
  Verschiebung des Grün-Rot-Spektrums auf eine kontraststarke Blau-Bernstein-Achse (Rot = Signal-Rubin, Grün = Signal-Königsblau), sodass Protanopie, Deuteranopie und Tritanopie ohne Informationsverlust unterstützt werden.

---

## 3. Informationsarchitektur & Routing-Struktur

### 3.1 Die 4 Säulen & URL-Mapping

Salus konsolidiert 31 Einzelrouten in **4 intuitive Hauptdomänen**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       SALUS 2.0 ROUTING TREE                                          │
├──────────────────────┬──────────────────────────┬────────────────────────────┬─────────────────────────┤
│ 1. ☀️ HEUTE (`/`)    │ 2. 📊 TRACK (`/track/*`) │ 3. 🧠 INSIGHTS (`/insights`│ 4. ⚙️ HUB & EINSTELLUNG │
├──────────────────────┼──────────────────────────┼────────────────────────────┼─────────────────────────┤
│ • Tages-Cockpit      │ • `/track` (Übersicht)   │ • `/insights` (Übersicht)  │ • `/hub/goals` (Ziele)  │
│ • Chrono-Timeline    │ • `/track/metrics`       │ • `/insights/trends`       │ • `/hub/community`      │
│ • Progress-Ringe     │ • `/track/workouts/*`    │ • `/insights/circadian`    │ • `/settings/account`   │
│ • Live-Status Leiste │ • `/track/nutrition/*`   │ • `/insights/forecast`     │ • `/settings/shares`    │
│                      │ • `/track/fasting`       │ • `/insights/coach` (Chat) │ • `/settings/sources`   │
│                      │ • `/track/habits/*`      │ • `/insights/data-quality` │ • `/settings/app`       │
│                      │ • `/track/labs`          │                            │ • `/admin/*`            │
│                      │ • `/track/medications/*` │                            │                         │
│                      │ • `/track/mental` (Mood) │                            │                         │
└──────────────────────┴──────────────────────────┴────────────────────────────┴─────────────────────────┘
```

*Hinweis zu Abwärtskompatibilität & Weiterleitungen:*  
Bestehende URLs wie `/entries`, `/habits`, `/meals`, `/fasting`, `/mood`, `/analytics`, `/goals` werden transparent per HTTP/SPA-Redirect auf ihre neuen kanonischen Pfade umgeleitet.

---

### 3.2 Responsive Shell (Desktop vs. Tablet vs. Mobile)

#### A. Desktop-Shell (≥ 1024px)
```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Logo] salus     [ ☀️ Heute ]  [ 📊 Track ]  [ 🧠 Insights ]  [ 🏆 Hub ]      [ 🔍 Cmd+K ] [ + Log ] [🔔] [👤]│
├───────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│   INHALTSBEREICH (Maximalbreite 1440px, zentriert, responsive 12-Spalten-Raster)                       │
│                                                                                                       │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
- **Fokusierte Top Bar:** Nur 4 Hauptreiter. Kein Dropdown-Überlauf.
- **Header-Aktionen:** Quick Search (`Cmd+K`), prominenter `+ Loggen` Button, Benachrichtigungen mit Badge, Profilmenü mit Live-Sync-Pille.

#### B. Mobile PWA Shell (< 1024px)
```
┌────────────────────────────────────────────────────────┐
│  ☀️ Guten Morgen, Philipp!                  [🔔] [👤]  │
│  Montag, 17. August 2026                 [● Live Sync] │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SCROLLBARER TAGES-INHALT                              │
│  (Hero-Ringe, Chrono-Timeline, Interaktive Kacheln)    │
│                                                        │
├────────────────────────────────────────────────────────┤
│  [ ☀️ Heute ]  [ 📊 Track ]   ( ➕ )   [ 🧠 Insights ] [ ⚙️ Hub ]│
└────────────────────────────────────────────────────────┘
```
- **Daumen-Navigation:** 4 Tabs + zentrierter, leicht überhöhter **Universal Quick-Log Button (`+`)**.
- **Vollständige Safe-Area-Unterstützung:** Berücksichtigung von iOS Home-Bar (`env(safe-area-inset-bottom)`) und Statusleiste.

---

### 3.3 Tastatur-Steuerung & Command Palette (`Cmd+K`)

Für Power-User und Desktop-Effizienz verfügt Salus über eine globale Schnell-Steuerung:
- **`Cmd + K` / `Ctrl + K`:** Öffnet die Command Palette (Suche nach Lebensmitteln, Übungen, Metriken, Zielen, Einstellungen).
- **`L` (außerhalb von Inputs):** Öffnet sofort den Quick-Log Hub.
- **`W`:** Direktes Starten eines Workouts.
- **`Left / Right`:** Tag zurück / vorwärts im Dashboard.
- **`T`:** Zurück zu „Heute“.

---

## 4. Der Universal Quick-Log Hub (Zero-Friction Capture)

Der Quick-Log Hub ist das funktionale Herzstück der Datenerfassung. Er öffnet sich als animiertes **Bottom Sheet (Mobile)** bzw. **zentriertes Fokus-Modal (Desktop)**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  SCHNELLERFASSUNG                                                                    [×]│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  1-TAP SCHNELLAKTIONEN:                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────────────┐ │
│  │ 💧 WASSER            │  │ 😊 STIMMUNG          │  │ 🔥 HABIT ABHAKEN               │ │
│  │ [+250ml] [+500ml]    │  │ [ 1 ][ 2 ][ 3 ][ 4 ] │  │ [✓] 3L Wasser getrunken        │ │
│  │ (+ Benutzerdefiniert)│  │ [ 5 - Fantastisch! ] │  │ [ ] 10.000 Schritte           │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  SCHNELLFORMULARE:                                                                      │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────────────┐ │
│  │ ⚖️ KÖRPERGEWICHT     │  │ ❤️ BLUTDRUCK / PULS  │  │ 🥗 MAHLZEIT ERFASSEN           │ │
│  │ [ 82.4 ] kg          │  │ [ 120 ] / [ 80 ] mmHg│  │ [ 🔍 Zutat/Barcode tippen... ] │ │
│  │ [ Speichern ]        │  │ Puls: [ 64 ] bpm     │  │ [ + Aus Favoriten / Vorlagen ] │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  WEITERE DISZIPLINEN:                                                                   │
│  [ 🏃 Workout starten ]   [ ⏳ Fasten starten ]   [ 💊 Medikament loggen ]   [ ✍️ Notiz ]│
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Interaktions-Details des Quick-Logs:
1. **Wasser-Logging:** Ein Klick auf `+250ml` erzeugt eine lokale Haptik/Animation, erhöht den Zähler sofort in Dexie und schließt das Sheet nach 600ms (oder erlaubt Mehrfach-Taps).
2. **Gewicht / Blutdruck:** Das Nummernfeld fokussiert sich automatisch mit Ziffernblock auf Mobilgeräten. Ein Druck auf Enter/Speichern speichert den Messwert.
3. **Mahlzeit:** Inline-Suche in der Food-DB mit Nährwert-Sofortvorschau, ohne den Nutzer auf eine neue Seite zu zwingen.

---

## 5. Detaillierte Screen-by-Screen-Spezifikation

---

### 5.1 Säule 1: Heute / Dashboard (`/`) — Das voll-anpassbare Cockpit

#### 5.1.1 Philosophie & Kernprinzip: Maximale Nutzer-Autonomie
Das Dashboard ist **kein statisches Layout**, sondern eine **100% modular konfigurierbare Arbeitsfläche**, die der Nutzer vollständig nach seinen persönlichen Prioritäten, Zielen und Vorlieben zusammenstellen kann.

Das zugrundeliegende Datenmodell (`db.dashboard_widget`) speichert für jede Kachel:
- `id`: Eindeutige UUID
- `widget_type`: Typ des Widgets (`metric` für jede beliebige Metrik oder spezifische Funktions-Widgets wie `workout_launcher`, `fasting_timer`, `water_logger`, `habit_strip`, `sleep_coach`, `circadian_timeline`, `macro_summary`, `medication_doses`)
- `metric_code`: Referenz auf `MetricDefinition.code` (z. B. `steps`, `heart_rate`, `weight`, `blood_pressure`, `glucose`, `hrv`)
- `size`: Rastergröße (`small` = 2 Spalten / 1/3 Breite, `medium` = 3 Spalten / 1/2 Breite, `large` = 6 Spalten / volle Breite)
- `position`: Integer für die exakte Sortierreihenfolge
- `is_visible`: Ein-/Ausblenden ohne Datenverlust
- `config_json`: Zusätzliche kachelspezifische Einstellungen (z. B. primärer Zeitraum, Diagrammtyp, Zielwerte)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ ☀️ Guten Morgen, Philipp                          [ < Gestern | HEUTE, 17. Aug | Morgen > ]│
│                                                   [ 📐 Layout anpassen ] [ ➕ Widget ]  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [OPTIONAL] HERO: TAGES-STATUS & PULSE (Ein-/Ausblendbar)                                │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │  ┌───────────────┐   ┌────────────────────────────────────────────────────────────┐ │ │
│ │  │  ( 84% RING ) │   │ 🟢 OPTIMALER ZUSTAND                                       │ │ │
│ │  │  Aktivität    │   │ • Schlaf: 7h 45m (+15m vs. Schnitt, Erholung exzellent)    │ │ │
│ │  │  Wasser       │   │ • Fasten: Noch 1h 45m bis Essensfenster (16h Ziel)        │ │ │
│ │  │  Habits       │   │ • Zirkadian: Fokus-Phase bis 12:30 • Koffein bis 14:00     │ │ │
│ │  └───────────────┘   └────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [OPTIONAL] LIVE-AKTIVITÄT: LÄUFT GERADE (Pulsierend, schwebend)                         │
│ ⏳ FASTEN LÄUFT • 14h 15m / 16h00m • [ Fasten beenden ]                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ MODULARES WIDGET-RASTER (Frei anordenbar per Drag & Drop in 6-Spalten-Raster)           │
│                                                                                         │
│ ┌──────────────────────┐ ┌──────────────────────┐ ┌───────────────────────────────────┐ │
│ │ 🚶 SCHRITTE (Medium) │ │ ❤️ RUHEPULS (Small)  │ │ 💧 HYDRATION (Small)              │ │
│ │ 8.420 / 10.000       │ │ 58 bpm               │ │ 2.250 / 3.000 ml                  │ │
│ │ ██████████████░ 84%  │ │ ↘ -3 bpm vs. 7T-Avg  │ │ [+250ml] [+500ml]                 │ │
│ └──────────────────────┘ └──────────────────────┘ └───────────────────────────────────┘ │
│ ┌───────────────────────────────────────────────┐ ┌───────────────────────────────────┐ │
│ │ 🥗 KALORIEN & MAKROS (Medium)                 │ │ 🔥 HEUTIGE GEWOHNHEITEN (Medium)  │ │
│ │ 1.840 / 2.400 kcal (P: 140g, C: 180g, F: 52g) │ │ [✓] Morgen-Dehnen  [✓] Meditation │ │
│ │ [ ████████████░░░░░░ ] 76%                    │ │ [✓] Vitamine       [ ] Lesen      │ │
│ └───────────────────────────────────────────────┘ └───────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 🌙 SCHLAF- & RECOVERY-ANALYSE (Large - Volle Breite)                                │ │
│ │ 7h 45m Gesamtschlaf • 1h 40m Tiefschlaf • 2h 10m REM • HRV: 62ms                    │ │
│ │ [ ▂▃▅▆▇██▇▆▅▃▂ ] Schlafphasen-Verlauf über die Nacht                                │ │
│ └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.1.2 Die Widget-Customization Engine (Interaktions-Ablauf)

1. **Direkt-Manipulation & Edit-Modus:**
   - Ein Klick auf `Layout anpassen` (oder langes Drücken auf Mobilgeräten) schaltet das Grid in den **Live-Edit-Modus**:
     - Kacheln erhalten einen dezenten Schwebe-Effekt und einen klaren Drag-Griff (`widget-chrome-handle`).
     - **Direktes Größen-Umschalten:** An jeder Karte befindet sich ein Größen-Selector (`[S] 1/3` | `[M] 1/2` | `[L] Voll`), der die Spaltenbreite sofort umschaltet.
     - **Freies Verschieben (Sortable.js):** Kacheln können flüssig an jede beliebige Position gezogen werden. Die neuen Positionen werden sofort lokal in Dexie persistiert und via Outbox synchronisiert.
     - **Entfernen / Verbergen:** 1-Klick auf das `Mülleimer`/`Auge`-Icon blendet die Kachel aus.

2. **Der Visuelle Widget-Katalog (Add-Drawer):**
   - Ein Klick auf `+ Widget hinzufügen` öffnet einen übersichtlichen Katalog mit **Live-Vorschau**:
     - **Kategorie Vitalwerte:** Ruhepuls, Blutdruck, Blutzucker, Sauerstoffsättigung, Körpertemperatur, HRV, Atemfrequenz.
     - **Kategorie Körper:** Gewicht, Körperfettanteil, Muskelmasse, Taillenumfang.
     - **Kategorie Fitness & Aktivität:** Schritte, Distanz, Aktive Kalorien, *Workout Launcher*.
     - **Kategorie Ernährung & Hydration:** *Wasser-Tracker*, *Makro-Split*, *Kalorien-Budget*.
     - **Kategorie Erholung & Zirkadian:** *Zirkadiane Timeline*, *Schlaf-Coach*, *Schlafdauer*, *Schlafschuld*.
     - **Kategorie Lifestyle & Disziplin:** *Habit-Checkliste*, *Fasten-Timer*, *Medikamenten-Dosen*, *Stimmungs-Picker*.
   - Vor dem Hinzufügen wählt der Nutzer direkt die gewünschte Startgröße (`Klein`, `Mittel`, `Groß`) und sieht, wie die Kachel mit seinen echten Daten aussehen wird.

3. **Vorkonfigurierte Dashboard-Profile (Templates):**
   - Für den schnellen Einstieg kann der Nutzer aus intelligenten Vorlagen wählen oder sein Dashboard mit 1 Klick zurücksetzen:
     - **„Kraftsport & Muskelaufbau“:** Fokus auf Workout Launcher, Makronährstoffe, Proteinziel, Körpergewicht und Erholung.
     - **„Longevity & Zirkadiane Gesundheit“:** Fokus auf Fasten-Timer, Zirkadiane Timeline, Blutdruck, HRV und Schlafqualität.
     - **„Alltag & Gewohnheiten“:** Fokus auf Hydration, Schrittzähler, Habit-Checkliste und Medikamente.
     - **„Minimalist“:** Nur die 3 Tages-Ringe und die wichtigsten 2 Metriken.
     - **„Blank Canvas“:** Völlig leere Arbeitsfläche für individuelle Gestaltung von Grund auf.

#### 5.1.3 Zustände & Edge-Cases des Dashboards:
- **Loading State:** Shimmering Skeleton-Karten in exakter Kachelgröße der benutzerdefinierten Widgets (kein Springen oder Layout-Shift).
- **Empty State (Keine Widgets konfiguriert):** Eine freundliche Einladung mit Direkt-Button zum Widget-Katalog oder Template-Wähler.
- **Tageswechsel:** Wischen oder Pfeiltasten ändern das Datum `displayDate`; alle Kacheln aktualisieren ihre Werte blitzschnell reaktiv über Dexie `useQuery`.

---

### 5.2 Säule 2: Track & Body (`/track/*`)

Zentrale Übersicht für alle Messwerte, Protokolle und Trainingsdaten.

---

#### 5.2.1 Metriken- & Vitalwerte-Logbuch (`/track/metrics`)
- **Struktur:** 
  - Filterbare Kategorien: *Kardiovaskulär*, *Körperzusammensetzung*, *Schlaf*, *Aktivität*, *Alle*.
  - Jede Metrik-Karte zeigt: Letzter Wert, Zeitstempel, 7-Tage-Sparkline, Trend-Delta.
- **Detailansicht (`/track/metrics/[code]`):**
  - **Interaktiver Hauptchart:** Umschaltbar zwischen Linear, Spline und Candlestick. Zeitraum-Wähler (`7T`, `30T`, `90T`, `1J`, `Max`).
  - **Statistik-Grid:** Minimalwert, Maximalwert, 7-Tage-EMA, Standardabweichung.
  - **Verlaufstabelle:** Tabellarische Auflistung aller Einzelmessungen mit Inline-Bearbeitung (`Bleistift-Icon`), Löschung und Quellen-Badge (`Manuell`, `Apple Health`, `Garmin`).
  - **Kombinierte Metriken (z.B. Blutdruck):** Synchroner Verlauf für Systolisch & Diastolisch in einem Chart mit farbig hinterlegtem optimalen Korridor (120/80 mmHg).

---

#### 5.2.2 Workouts & Krafttraining (`/track/workouts/*`)
- **Unterbereiche:**
  1. **Übersicht (`/track/workouts`):** Letzte Sessions, wöchentliches Volumen (kg), Split-Verteilung, Schnellauswahl für Pläne.
  2. **Trainingspläne (`/track/workouts/plans`):** Liste aller Pläne (Push/Pull/Legs, Upper/Lower, Ganzkörper).
  3. **Plan-Editor (`/track/workouts/plans/[id]`):** Drag-and-Drop Übungsreihenfolge, Ziel-Sätze, Ziel-Wiederholungen, Pausenzeiten, Supersatz-Gruppierung.
  4. **Übungsdatenbank (`/track/workouts/exercises`):** Durchsuchbar nach Muskelgruppen (mit interaktiver SVG-Körperkarte: Brust, Rücken, Quadrizeps etc.), Equipment und Schwierigkeit.
  5. **Übungs-Detail (`/track/workouts/exercises/[id]`):** 1RM-Berechnung (Epley/Brzycki Formel), historischer Volumen-Verlauf, persönliche Rekorde (PRs).
- **Live Active Session Mode (`/track/workouts/active`):**
  - **Sticky Header:** Trainingszeit, Gesamtvolumen (kg), beendete Sätze.
  - **Übungs-Karte:**
    - Zeigt den vorherigen Satz aus dem letzten Training als Referenz (*"Letztes Mal: 80kg × 10"*).
    - **Große Eingabefelder:** Schnelle Satz-Bestätigung mit 1 Klick.
    - **RPE-Chip-Leiste (1–10):** Autoreguliertes Feedback.
    - **Automatischer Rest-Timer:** Startet nach Satz-Häkchen sofort einen schwebenden Countdown-Balken mit Signalton / Vibration bei 0.

---

#### 5.2.3 Ernährung & Food-Tracking (`/track/nutrition/*`)
- **Tages-Makro-Übersicht:**
  - Kalorien-Ring: Verbraucht vs. Ziel vs. Verbleibend.
  - 3-Balken-Makro-Split: Protein, Kohlenhydrate, Fett mit Gramm- und Prozentangaben.
- **Mahlzeiten-Gruppen:** Frühstück, Mittagessen, Abendessen, Snacks, Pre/Post-Workout.
- **Lebensmittel-Erfassung (Modal / Inline):**
  - Instant-Suche mit Nährwert-Badge (kcal, P, C, F pro 100g).
  - Portions-Wähler mit gängigen Maßeinheiten (Gramm, Portion, Stück, Esslöffel).
  - Barcode-Scanner Unterstützung für mobile Endgeräte.
- **Rezept-Manager (`/track/nutrition/recipes`):**
  - Erstellung von Rezepten aus mehreren Zutaten.
  - Automatische Berechnung von Gesamtgewicht, Portionsgröße und Nährwerten pro Portion.

---

#### 5.2.4 Fasten-Tracker (`/track/fasting`)
- **Visual Fasting Ring:** 
  - Kreisanzeige mit aktuellem Fortschritt, verbleibender Zeit und Zielzeitpunkt.
  - **Stoffwechsel-Phasen-Skala:**
    - 0–4h: Blutzucker-Normalisierung
    - 4–12h: Glykogen-Abbau & Insulin-Senkung
    - 12–18h: Fettverbrennung & Ketose-Start
    - 18–24h: Autophagie & zelluläre Regeneration
    - >24h: Tiefen-Autophagie
- **Fasten-Protokolle:** 16:8 (Intermittent), 18:6, 20:4 (Warrior), OMAD (23:1), Benutzerdefiniert / Freies Fasten.
- **Fasten-Historie:** Kalender-Heatmap der geführten Fastenperioden mit Erfolgsrate.

---

#### 5.2.5 Gewohnheiten (Habits & Streaks) (`/track/habits/*`)
- **Tages-Checkliste:**
  - Jede Gewohnheit mit Icon, Name, Zielanzahl und Streak-Flamme.
  - Große, haptische Check-Buttons mit animierter Vollzugs-Grafik.
- **Detailansicht (`/track/habits/[id]`):**
  - Jahres-Heatmap (GitHub-Style 365-Tage-Matrix).
  - Statistiken: Aktueller Streak, Längster Streak, Gesamterfüllungsrate (%).
  - Habit-Stacking Notiz (*"Wann & Wo wird diese Gewohnheit ausgeführt?"*).

---

#### 5.2.6 Klinische Labordaten (`/track/labs`)
- **Panel-Organisation:** Großes Blutbild, Lipid-Panel, Hormone & Schilddrüse, Stoffwechsel & Nieren, Vitamine & Mineralien.
- **Visuelle Referenzbereich-Leiste (`LabRangeBar`):**
  - Horizontale Leiste mit 4 definierten Zonen: `Niedrig` (Gelb/Rot), `Optimal` (Grün), `Erhöht` (Gelb), `Kritisch` (Rot).
  - Eine markante Messwert-Nadel mit exaktem Wert und Einheit (z.B. *Ferritin: 145 µg/l*).
- **Historischer Biomarker-Trend:** Vergleich über mehrere Blutabnahmen hinweg in einer Zeitreihe.

---

#### 5.2.7 Medikamente & Supplemente (`/track/medications/*`)
- **Tages-Dosis-Zeitplan:** Nach Uhrzeiten geordnete Einnahme-Karten (Morgens, Mittags, Abends, Vor dem Schlafen).
- **1-Tap-Einnahme-Häkchen:** Direkte Bestätigung oder *„Überspringen“* mit Grund.
- **Inventar-Tracker:** Warnung bei niedrigem Restbestand (*"Noch 6 Kapseln übrig – Nachbestellen"*).
- **Adhärenz-Statistik:** Monatliche Einnahme-Treuequote (%).

---

#### 5.2.8 Mental Health (Mood & Journal) (`/track/mental/*`)
- **Stimmungs-Check-in:** 
  - 2-Dimensionales Valenz-/Erregungs-Raster (oder 5-Punkte-Skala) + optionale Tags (*Fokussiert, Gestresst, Dankbar, Müde, Motiviert*).
- **Tagebuch (Journal):** 
  - Markdown-Editor mit Fokusmodus.
  - Tägliche Reflexionsfragen (*"Wofür bist du heute dankbar?", "Was war die größte Erkenntnis?"*).
  - Volltextsuche und Stimmungs-Korrelations-Tagging.

---

### 5.3 Säule 3: Insights & Intelligence (`/insights/*`)

Die wissenschaftliche Analyse-Zentrale von Salus.

---

#### 5.3.1 Globale Trends & Korrelations-Matrix (`/insights/trends`)
- **Interaktive Korrelations-Matrix:**
  - Berechnet Zusammenhänge zwischen zwei beliebigen Faktoren (z.B. *Schritte vs. REM-Schlaf*, *Koffein-Uhrzeit vs. Einschlafdauer*, *Proteingehalt vs. Kraftzuwachs*).
  - Umschaltung der statistischen Methode: **Pearson** (linear) vs. **Spearman** (Rangkorrelation).
  - Verständliche Klartext-Synthese: *„Signifikanter Zusammenhang (r = +0.68, p < 0.01): An Tagen mit über 8.000 Schritten schläfst du im Schnitt 32 Minuten länger.“*
- **Multi-Metrik-Vergleich:** Übereinanderlegen von zwei beliebigen Kurven auf zwei Y-Achsen (z.B. Ruhepuls vs. Trainingsvolumen).

---

#### 5.3.2 Zirkadianer Coach & Rhythmus-Uhr (`/insights/circadian`)
- **24-Stunden-Zirkadianuhr (`CircadianDial`):**
  - Dynamisch berechnet anhand der Aufwachzeit und Sonnenzeiten des Nutzers.
  - **Farbcodierte Zeitfenster:**
    - 🌅 **Licht-Expositions-Fenster:** Erste 60 Minuten nach dem Aufwachen.
    - ⚡ **Kognitiver Peak:** 2–4 Stunden nach dem Aufwachen (optimale Zeit für schwere Arbeit).
    - ☕ **Koffein-Cutoff:** Exakt 8–10 Stunden vor der Ziel-Schlafenszeit.
    - 🏃 **Optimales Trainingsfenster:** Später Nachmittag (Körperkerntemperatur am höchsten).
    - 🌙 **Melatonin- & Wind-Down-Phase:** 90 Minuten vor dem Schlafen (Blaulichtfilter / Dimmen).

---

#### 5.3.3 Forecast Lab (Prognose-Simulator) (`/insights/forecast`)
- **Interaktiver Gewichts- & Körperfett-Simulator:**
  - Schieberegler für tägliches Kaloriendefizit / Überschuss (-1000 bis +1000 kcal).
  - Mathematische Projektionskurve über 30, 60, 90 und 180 Tage basierend auf der metabolischen Konstante ($7.700\text{ kcal}/\text{kg}$ Fettgewebe) und adaptivem TDEE.
  - Visueller Vergleich zwischen tatsächlichem Verlauf und Modellkurve.

---

#### 5.3.4 KI-Gesundheitscoach (Chat) (`/insights/coach`)
- **Kontextueller Chat-Assistent:**
  - Kennt die lokalen Gesundheitsdaten der letzten Wochen (unter strikter Privatsphäre / Local-First).
  - Kann Fragen beantworten wie: *„Wie hat sich mein Schlaf seit Beginn der Fastenphase verändert?“* oder *„Erstelle mir einen Plan zur Reduktion meines Blutdrucks.“*
  - Schnellauswahl für vorgefertigte Coaching-Prompts.

---

#### 5.3.5 Datenqualitäts-Inspektor (`/insights/data-quality`)
- **Automatisierte Datenhygiene:**
  - Erkennt Ausreißer (z.B. Tippfehler wie 850 kg statt 85.0 kg), doppelte Einträge und Zeitzonen-Konflikte.
  - 1-Klick-Reparatur- und Bereinigungsassistent.

---

### 5.4 Säule 4: Hub, Community & Settings (`/hub/*` & `/settings/*`)

---

#### 5.4.1 Ziele, Meilensteine & Mathematische Prognosen (`/hub/goals`)

##### A. Datenmodell & Mathematischer Unterbau
Das Salus Goal-System (`models/goal.py` & `goal-views.ts`) unterstützt:
- **Zielrichtungen (`GoalDirection`):** `increase` (z. B. Schritte, Muskelmasse, Wasser, Protein) vs. `decrease` (z. B. Körpergewicht, Körperfett, Blutdruck, Schlafschuld).
- **Frequenzen (`GoalFrequency`):** `daily` (tägliche Zielwerte), `weekly` (Wochenziele) und `once` (Stichtags-Ziele mit festem `deadline`-Datum).
- **Ernährungs-Ziele (`NutritionField`):** Direkte Bindung an `calories`, `protein`, `carbs` und `fat`.
- **Statistische Deadline-Prognose (Lineare Regression & 80% Konfidenzintervall):**
  - `linearRegression(xs, ys)` berechnet die historische Veränderungsrate und das Bestimmtheitsmaß $R^2$.
  - `predictionInterval(reg, daysTotal, 0.8)` berechnet die Punktschätzung am Zieldatum sowie das untere (`ci_lower`) und obere (`ci_upper`) 80%-Konfidenzband.
  - **Status-Klassifikation:** `on_track` (Prognose trifft Ziel im Konfidenzintervall), `ahead` (übertrifft Ziel), `behind` (erfordert Geschwindigkeitsanpassung), `achieved` (bereits erreicht).

##### B. Domänenübergreifende Integration von Zielen
Ziele existieren nicht isoliert, sondern fließen in jeden relevanten Bereich ein:
1. **Dashboard-Widgets:** Metrik-Kacheln (z. B. Schritte, Wasser, Kalorien) blenden automatisch Ziel-Fortschrittsbalken und Prozentwerte ein.
2. **Logbuch- & Detail-Charts (`/track/metrics/[code]`):** Eine dezente gestrichelte Ziel-Linie im Chart visualisiert die Zielmarke und den projizierten Kurs.
3. **Ernährungs-Zentrale (`/track/nutrition`):** Kalorien- und Makro-Ziele steuern die Tagesbudgets und Warnschwellen.
4. **Detailansicht (`/hub/goals/[id]`):**
   - **Prognose-Trichter:** Visualisierung der historischen Messwerte mit linearer Regressionsgerade und auffächerndem 80%-Konfidenztrichter bis zum Zieldatum.
   - **Geschwindigkeits-Anzeige (Pace / Velocity):** *"Benötigte Veränderung: -0.45 kg / Woche, um das Ziel bis zum 15. Oktober zu erreichen (Aktuelle Geschwindigkeit: -0.52 kg / Woche • Im Plan)."*
   - **Meilenstein-Checkliste:** Automatisch in 25%-, 50%- und 75%-Etappen unterteilte Meilensteine mit Erreicht-Datum.

---

#### 5.4.2 Achievements & Trophäen-System (`/hub/achievements`)
- **Trophäen-Kategorien:** *Konsistenz & Streaks*, *Aktivität & Volumen*, *Ernährung & Fasten*, *Daten-Pionier*.
- **Fortschritts-Tracking:** Unvollendete Achievements zeigen einen klaren prozentualen Balken (z. B. *"30-Tage Fasten-Streak: 21 / 30 Tage geschafft"*).
- **Ästhetische Badges:** Hochwertige Vektorgrafiken ohne kindischen Kitsch – visualisiert als edle geometrische Medaillen.
- **Aktivitäts-Feed:** Anonymisierte oder geteilte Erfolge von Freunden.
- **Freundschafts-Leaderboard:** Wöchentliche Challenges (z.B. Schritte, Workout-Volume) mit datenschutzkonformen Rängen.

---

#### 5.4.3 E2EE-Freigaben & Sharing (`/settings/shares`)
- **Ende-zu-Ende-verschlüsselte Arzt-/Trainer-Freigaben:**
  - Asymmetrisch verschlüsselte Links mit Ablaufdatum und Passwortschutz.
  - Granulare Auswahl: *„Nur Blutdruck und Labore der letzten 90 Tage teilen“*.
  - Zugriffsprotokoll (wer hat wann welche Daten abgerufen).

---

#### 5.4.4 Geräte, Quellen & Datenexport (`/settings/sources`)
- **Gerätestatus & Integrationen:** Apple Health, Garmin, Oura, Polar, Webhooks.
- **Datenexport:**
  - Strukturierter CSV- / JSON-Export aller Tabellen.
  - **Klinischer PDF-Gesundheitsbericht:** Professionell gestaltetes PDF für den Arztbesuch mit Vitalwerte-Übersicht, Laborwert-Verläufen und Medikamentenplan.

---

#### 5.4.5 Account, Sicherheit & App-Konfiguration (`/settings/app`)
- **Theme- & Farb-Einstellungen:** Heller / Dunkler Modus, dynamischer Akzent-Hue (0–360°), Kontrast- & Farbfehlsichtigkeits-Optionen.
- **Biometrische Sperre (PWA/Mobile):** Fingerabdruck / Face Unlock beim Öffnen der App.
- **Sync-Status & IndexedDB Speicherverbrauch:** Transparente Anzeige lokaler Datensätze und Cache-Verwaltung.

---

## 6. Das Grafische Visualisierungs- & Illustrierte Komponenten-System (*Visual Delight Engine*)

Gesundheitstracking wird erst dann lebendig, motivierend und intuitiv verständlich, wenn Daten nicht nur als nackte Ziffern, sondern als **dynamische, ästhetische Vektorgrafiken und visuelle Metaphern** dargestellt werden.

Salus 2.0 etabliert ein dediziertes, domänenspezifisches Grafiksystem:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SALUS 2.0 VISUAL GRAPHICS MATRIX                                      │
├──────────────────────┬──────────────────────────────────────────┬──────────────────────────────────────┤
│ Domäne / Feature     │ Grafische Visualisierungs-Komponente     │ Visuelle Metapher & Interaktion      │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Hydration**        │ `HydrationWaveGlass.svelte`              │ Füllendes SVG-Glas mit animierten    │
│                      │                                          │ Wellen & Bläschen je nach ml-Stand   │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Fasten**           │ `FastingMetabolicClock.svelte`           │ Kreisförmiger Farbverlaufs-Timer mit │
│                      │                                          │ leuchtenden Stoffwechsel-Zonen       │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Zirkadian**        │ `CircadianSunArc.svelte`                 │ 24h-Himmelsbogen mit Sonnen-/Mond-   │
│                      │                                          │ Zeiger und kognitiven Peak-Zonen     │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Workouts**         │ `MuscleHeatmap2D.svelte`                 │ Anatomisches SVG-Körpermodell        │
│                      │                                          │ (Front/Back) mit 7-Tage-Volumen-Heat │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Schlaf**           │ `SleepHypnogram.svelte`                  │ Weiche Flächenkurve für Schlafphasen │
│                      │                                          │ (Tief, REM, Leicht, Wach) + Zyklen   │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Ernährung**        │ `MacroDonutGauge.svelte`                 │ Dreifach verschachtelte Glow-Ringe   │
│                      │                                          │ für Protein, Carbs, Fett + Kalorien  │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Labore**           │ `ClinicalGaugeMeter.svelte`              │ Farbiger Halbkreis-/Balken-Tacho     │
│                      │                                          │ mit Präzisions-Nadel & Normalzone    │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Mental / Mood**    │ `MoodValenceSphere.svelte`               │ 2D-Farbgradienten-Kugel, die sich    │
│                      │                                          │ je nach Energie & Valenz verformt    │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Achievements**     │ `AchievementMedalVector.svelte`          │ Geometrische Vektor-Medaillen mit    │
│                      │                                          │ radialem Lichtburst bei Freischaltung│
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Widget-Galerie**   │ `WidgetGalleryCard.svelte`               │ Miniaturisierte Live-Vorschau jedes  │
│                      │                                          │ Widgets mit echten animierten Daten  │
└──────────────────────┴──────────────────────────────────────────┴──────────────────────────────────────┘
```

### 6.1 Detail-Spezifikation der visuellen Komponenten

#### 1. `HydrationWaveGlass.svelte` (Interaktive Wasser-Grafik)
- Ein eleganter SVG-Becher mit transparenter Glasur.
- Zwei gegenläufig oszillierende SVG-Sinuswellen mit leichtem Gradienten füllen das Glas millimetergenau entsprechend dem aktuellen ml-Stand.
- Bei Tipp auf `+250ml` strömen kleine aufsteigende Partikel/Bläschen nach oben, begleitet von einer dezenten Wasser-Puls-Animation.

#### 2. `FastingMetabolicClock.svelte` (Stoffwechsel-Phasen-Uhr)
- 360°-Kreisdiagramm mit lebendigen Leuchtspuren:
  - Phase 1 (0–4h): Blassblau (Glukose-Verwertung)
  - Phase 2 (4–12h): Türkis (Glykogen-Entleerung)
  - Phase 3 (12–18h): Bernstein/Gold (Fettverbrennung & Ketose)
  - Phase 4 (18–24h): Tiefes Violett/Smaragd (Autophagie & Zellreinigung)
- Im Zentrum: Ein präziser Countdown (*"Noch 1h 42m bis 16h"*) mit pulsierendem Fortschrittspunkt.

#### 3. `MuscleHeatmap2D.svelte` (Anatomische Muskel-Heatmap)
- Vektorbasiertes Modell des menschlichen Körpers (Vorderseite und Rückseite umschaltbar).
- Alle Hauptmuskelgruppen (Brust, Latissimus, Trapez, Schultern, Bizeps, Trizeps, Bauch, Quadrizeps, Hamstrings, Waden, Gesäß) sind als eigenständige SVG-Pfade angelegt.
- Die Farbintensität (von neutralem Grau über warmes Gelb bis zu feurigem Korallenrot) skaliert exakt mit dem kumulierten Trainingsvolumen (kg) der letzten 7 Tage.

#### 4. `SleepHypnogram.svelte` (Schlafarchitektur-Diagramm)
- Glatte, interpolierte Spline-Fläche, die die Nachtphasen darstellt:
  - Wach (Hellgrau / Orange)
  - REM-Schlaf (Helles Violett)
  - Leichtschlaf (Mittleres Blau-Violett)
  - Tiefschlaf (Dunkles, sattes Indigo)
- Vertikale Zeitstempel und Markierung von Aufwach-Episoden.

#### 5. `WidgetGalleryCard.svelte` (Live-Vorschau im Widget-Katalog)
- Im Add-Widget Drawer sieht der Nutzer keine abstrakten Textkarten, sondern eine **vollständig animierte Miniatur-Version** des jeweiligen Widgets mit echten Daten.
- Der Nutzer sieht sofort: *„Wie verhält sich das Fasten-Widget auf Medium? Wie sieht der Muskel-Launcher auf Small aus?“*.

---

## 7. Lückenlose User Journey Flows (End-to-End Flows)

Damit Salus nicht nur schön aussieht, sondern im Alltag mühelos von der Hand geht, sind alle täglichen Interaktionen als **reibungslose, fließende User Journeys** konzipiert.

---

### Flow 1: Die Morgen-Routine (*Morning Awakening & Readiness*)
```
[ App öffnen / Widget ]
       │
       ▼
1. HERO-BEGRÜSSUNG: "Guten Morgen, Philipp" + Schlaf-Hypnogramm der Nacht
       │
       ▼
2. SCHLAF-RATING: 1-Tap Bewertung (Erholt? 1–5 Sterne)
       │
       ▼
3. READINESS-SYNTHESE: "Erholung: 92% • Optimaler Tag für schweres Training"
       │
       ▼
4. ZIRKADIANER IMPULS: "☀️ Ideales Sonnenlicht-Fenster: Die nächsten 45 Minuten"
       │
       ▼
5. HABIT-CHECK: Wischgeste über Morgen-Gewohnheiten (Wasser trinken, Dehnen)
       │
       ▼
6. FASTEN-STATUS: "Fasten läuft seit 13h 20m • Essensfenster öffnet um 12:30"
```
- **Dauer:** Unter 20 Sekunden.
- **Ergebnis:** Der Nutzer hat sofort Orientierung, Motivation und den Tagesfokus verinnerlicht.

---

### Flow 2: Das Krafttraining (*Live Active Session Mode*)
```
[ Workout Launcher im Dashboard / Quick-Log: "Training starten" ]
       │
       ▼
1. SPLIT-AUSWAHL: "Push Day A" (bereits vorgeschlagen basierend auf Plan)
       │
       ▼
2. LIVE SESSION SCREEN:
   • Oben: Sticky Timer, Gesamttonnage, Satz-Zähler
   • Übung 1: Bankdrücken
   • Satz 1: Zeigt Referenz aus letzter Woche ("Letztes Mal: 80kg × 10")
       │
       ▼
3. SATZ-LOGGEN: 1-Tap auf Gewicht/Reps Tastaturfeld -> Satz-Häkchen [ ✓ ]
       │
       ▼
4. AUTO-REST TIMER: Schwebender Kreisbalken zählt 90s herunter (Vibration bei 0s)
       │
       ▼
5. PR-CELEBRATION: Neuer Rekord? Subtiler Vektor-Funkenregen & Badge-Freischaltung
       │
       ▼
6. SESSION BEENDEN: Zusammenfassungs-Karte (Volumen, Rekorde, aktualisierte Muskel-Heatmap)
```
- **Fokus:** Keine Tastatur-Krämpfe während des Trainings. Riesige Touch-Ziffernfelder, automatischer Pausentimer.

---

### Flow 3: Ernährung & Hydration am Mittag (*Midday Fuel & Hydration*)
```
[ Quick-Log (+) oder Wasser-Kachel im Dashboard ]
       │
       ▼
1. HYDRATION: 1-Tap auf [+500ml] -> WaveGlass füllt sich animiert
       │
       ▼
2. FASTEN-ABSCHLUSS: Fasten-Ziel erreicht -> Feierliche Erfolgs-Animation [ Fasten beenden ]
       │
       ▼
3. MAHLZEIT ERFASSEN:
   • Option A: Barcode scannen (PWA Kamera)
   • Option B: Schnellsuche ("Hähnchenbrust mit Reis")
   • Option C: Aus gespeicherten Rezepten wählen
       │
       ▼
4. MAKRO-SPLIT UPDATE: Donut-Ringe aktualisieren sich sofort (Proteinbalken wächst)
```

---

### Flow 4: Abend-Reflexion & Schlaf-Vorbereitung (*Evening Wind-down*)
```
1. 14:30: KOFFEIN-CUTOFF HINWEIS: "Letzte Tasse Kaffee für optimalen Tiefschlaf"
       │
       ▼
2. 20:30: ABEND-CHECK-IN:
   • Stimmung erfassen (2D-Valenz-Raster)
   • 1–2 Sätze im Journal notieren (Optionale Leitfragen)
       │
       ▼
3. 21:30: MELATONIN-PHASE:
   • Dashboard schaltet sanft in den Nacht-Modus (Blaulicht-Reduktion)
   • Schlaf-Coach zeigt empfohlene Zubettgeh-Zeit (22:45)
```

---

### Flow 5: Arzt- & Trainer-Export (*Clinical Consultation & E2EE Sharing*)
```
[ Einstellungen -> Freigaben / PDF-Export ]
       │
       ▼
1. ZEITRAUM WÄHLEN: "Letzte 90 Tage"
       │
       ▼
2. DATENPUNKTE FILTERN: [✓] Blutdruck & Puls  [✓] Großes Blutbild  [✓] Medikamentenplan
       │
       ▼
3. AUSGABE-MODUS:
   • Modus A: Asymmetrisch verschlüsselter E2EE-Weblink mit PIN für den Arzt
   • Modus B: Hochauflösender, druckfertiger PDF-Klinikbericht mit Referenz-Tachos
```

---

## 8. Komponenten-Bibliothek & Datenvisualisierungs-Standards

### 8.1 Übersicht der neuen & modernisierten Kernkomponenten

```
┌───────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Komponente                │ Visuelle Spezifikation & Interaktionsverhalten                         │
├───────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ `MetricTile.svelte`       │ Kompakte Karte mit Icon, Display-Wert, Einheit, Trend-Pfeil, Sparkline │
│ `HeroProgressRings.svelte`│ 3 konzentrische SVG-Ringe mit fließenden Verläufen und Center-Icon     │
│ `CircadianSunArc.svelte`  │ 24h-Kreis-Timeline mit Zonen (Licht, Fokus, Koffein-Cut, Melatonin)   │
│ `HydrationWaveGlass.svelte│ Füllendes SVG-Wasserglas mit flüssigen Wellen & Partikel-Animation    │
│ `FastingMetabolicClock.sv`│ Radialer Stoffwechselphasen-Timer mit Glukose-, Ketose- & Autophagie   │
│ `MuscleHeatmap2D.svelte`  │ Anatomisches 2D-Muskelmodell (Front/Back) mit 7-Tage-Volumen-Heatmap   │
│ `SleepHypnogram.svelte`   │ Spline-Flächenkurve für Tief-, REM-, Leichtschlaf & Wachphasen         │
│ `MacroDonutGauge.svelte`  │ Konzentrische Glow-Ringe für Protein, Kohlenhydrate, Fett & Kalorien   │
│ `ClinicalGaugeMeter.svelte│ 4-Zonen-Tachometer mit Präzisions-Nadel für Biomarker-Referenzbereiche │
│ `QuickLogSheet.svelte`    │ Wischbares Bottom Sheet mit Ziffernblock und 1-Tap Log-Aktionen        │
│ `InteractiveChart.svelte` │ Hochpräzises SVG-Diagramm mit Scrubbing, Konfidenzband & Zoom          │
│ `HabitCheckCircle.svelte` │ Taktiler Check-Button mit SVG-Burst-Animation und Haptik-Trigger       │
│ `BottomNavBar.svelte`     │ Feste PWA-Navigationsleiste mit aktivem Glow und erhöhtem Center-FAB   │
│ `RestTimer.svelte`        │ Schwebender Workout-Countdown mit Pausieren, +30s und Signalton        │
│ `SegmentedControl.svelte` │ Schiebende Pillen-Auswahl mit federnder CSS-Animation                  │
│ `EmptyStatePro.svelte`    │ Stimmungsvoller leerer Zustand mit Illustration und primärem CTA       │
│ `SkeletonCard.svelte`     │ Shimmer-Ladeplatzhalter in exakter Ziel-Dimension                      │
└───────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Datenvisualisierung & Chart-Standards
1. **Zeitachsen-Standardisierung:**
   - Standard-Intervalle: `7D` (7 Tage), `30D` (30 Tage), `90D` (3 Monate), `1Y` (1 Jahr), `ALL` (Gesamt).
   - Wochentags-Markierungen bei 7D (`Mo, Di, Mi...`), Datums-Stempel bei 30D/90D (`12. Aug`).
2. **Glättung & Rauschunterdrückung:**
   - Bei stark schwankenden Werten (z. B. Körpergewicht durch Wasserhaushalt) wird standardmäßig ein **7-Tage-EMA (Exponential Moving Average)** als beruhigte Leitlinie eingeblendet.
3. **Scrubbing & Tooltips:**
   - Horizontales Ziehen mit der Maus oder dem Finger bewegt eine feine vertikale Haarlinie. Ein schwebender Glasmorphismus-Tooltip zeigt Datum, Exaktwert, Abweichung zum Vortag und optionalen Kontext (z. B. getätigte Mahlzeit oder Workout an diesem Tag).
4. **Ziel- & Schwellenwert-Bänder:**
   - Zielbereiche (z. B. Normalblutdruck 120/80 oder Zielschrittzahl 10.000) werden als sanft schattierte, halbtransparente Korridore im Hintergrund hinterlegt.

---

## 9. Zustands-Management & Edge Cases

```
┌──────────────────────┬─────────────────────────────────────────────────────────────────────────────┐
│ Zustand / Szenario   │ System-Verhalten & UI-Darstellung                                           │
├──────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ **Initiales Laden**  │ Keine Spinner-Überlagerung. Shimmer-Skeletons in exakter Kachelgröße.       │
│ **Offline-Betrieb**  │ Vollständige Funktionalität. Änderungen landen in Dexie-Outbox.             │
│                      │ Dezente Status-Pille im Header zeigt „Offline (3 Änderungen wartend)“.      │
│ **Sync-Konflikt**    │ Nicht-blockierender automatischer Abgleich; bei echtem Datenkonflikt        │
│                      │ öffnet sich der `ConflictDialog` mit Feld-für-Feld Vergleich.               │
│ **Session-Ablauf**   │ Kein harter Absturz. Subtiler Warn-Banner im Header mit 1-Klick Re-Login.   │
│ **Leere Datenstände**│ Keine toten Bildschirme: Motivierende Empty States mit konkreten Vorschlägen│
│                      │ und 1-Klick Erfassungs-Start.                                               │
│ **Extremwerte / Bug**│ Plausibilitäts-Warnung bei Eingabe (z.B. "Puls > 220 bpm - Tippfehler?").   │
└──────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Schrittweiser Migrations- & Implementierungsplan

Die Umsetzung erfolgt in **4 strikt voneinander abgegrenzten Phasen**, um jederzeitige Lauffähigkeit und Zero-Regression zu gewährleisten:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Design-Fundament & Globale Shell (Woche 1)                                     │
│ 1.1 Token-Überarbeitung in app.css (OKLCH-Farben, Radien, Shadows, Typo-Scale)         │
│ 1.2 Neue Navigation: TopAppBar.svelte (Desktop) & BottomNavBar.svelte (Mobile)          │
│ 1.3 Universal QuickLogSheet.svelte & Tastatur-Shortcut (Taste L / FAB)                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: Das "Heute" Cockpit (Dashboard) (Woche 2)                                      │
│ 2.1 Hero-Header mit Begrüßung, Datum-Navigation & Tages-Puls Ringe                     │
│ 2.2 Chronologische Zirkadian- & Tages-Timeline                                          │
│ 2.3 Überarbeitung der interaktiven Widget-Kacheln (Wasser, Fasten, Schritte, Habits)    │
│ 2.4 Visueller Widget-Katalog Drawer mit animierten Miniatur-Live-Vorschauen             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: Track & Body Zentrale (/track/*) (Woche 3)                                     │
│ 3.1 Zusammenführung von Metriken, Workouts, Food, Fasten, Habits und Labs unter /track  │
│ 3.2 Live Workout Active Mode mit MuscleHeatmap2D & Rest-Timer                           │
│ 3.3 Food & Recipe Manager mit visuellen MacroDonutGauges                                │
│ 3.4 ClinicalGaugeMeter für klinische Blutwerte & Referenzbereiche                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: Insights, Community & Polishing (Woche 4)                                      │
│ 4.1 CircadianSunArc & Korrelations-Matrix Redesign                                      │
│ 4.2 Forecast Lab & KI-Coach UI                                                          │
│ 4.3 Gesten (Swipe-to-Complete, Tag-Wischen) & haptisches Feedback                       │
│ 4.4 Klinischer PDF-Gesundheitsbericht für Ärzte                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Freigabe & Verbindlichkeit

Dieses Dokument ist die **vollständige, lückenlose architektonische Spezifikation für Salus 2.0**. Alle künftigen Komponenten, Routen und Design-Anpassungen orientieren sich ausnahmslos an den hier festgelegten Tokens, Routen, Grafiken und Interaktionsmustern.
