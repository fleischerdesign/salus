# Salus 2.0 — Tiefenspezifikation aller Domänen
**Dokument:** `06-domains-deep-dive.md`  
**Status:** Verbindlich

---

## 1. Säule 1: Heute / Dashboard (`/`) — Das modulare Cockpit

### 1.1 Die Widget-Customization Engine
Das Dashboard ist eine **vollständig anpassbare, modulare Arbeitsfläche**.

- **Datenmodell (`db.dashboard_widget`):** `id`, `widget_type`, `metric_code`, `size` (`small` = 1/3, `medium` = 1/2, `large` = Voll), `position`, `is_visible`, `config_json`.
- **Direkt-Manipulation (Edit-Modus):**
  - Klick auf `Layout anpassen` aktiviert Drag & Drop Griffe (`Sortable.js`).
  - Direkter Größen-Toggle (`[S] [M] [L]`) an jeder Kachel.
  - Ausblenden / Löschen mit 1 Klick.
- **Visueller Widget-Katalog Drawer:**
  - Miniaturisierte Live-Vorschauen (`WidgetGalleryCard.svelte`) mit echten Nutzerdaten.
  - Kategorien: *Vitalwerte*, *Körper*, *Fitness*, *Ernährung*, *Erholung*, *Lifestyle*.
- **Vorkonfigurierte Templates:** *„Kraftsport“*, *„Longevity & Fasten“*, *„Minimalist“*, *„Blank Canvas“*.

---

## 2. Säule 2: Track & Body (`/track/*`)

### 2.1 Metriken- & Vitalwerte-Logbuch (`/track/metrics`)
- **Übersicht:** Filterbar nach *Kardiovaskulär*, *Körperbau*, *Schlaf*, *Aktivität*.
- **Detail-Screen (`/track/metrics/[code]`):**
  - Interaktiver Spline-/Candlestick-Chart mit umschaltbaren Zeitfenstern (`7T`, `30T`, `90T`, `1J`, `Max`).
  - 7-Tage-EMA Glättungslinie & Konfidenzband.
  - Gestrichelte Ziel-Linie (`Goal`).
  - Historien-Tabelle mit Inline-Editierung, Löschung und Quellen-Badge (`Manuell`, `Apple Health`, `Garmin`).
  - Kombinierte Metriken (z. B. Blutdruck mit Systolisch/Diastolisch im 120/80 mmHg Norm-Korridor).

### 2.2 Workouts & Krafttraining (`/track/workouts/*`)
- **Pläne-Editor (`/track/workouts/plans/[id]`):** Drag-and-Drop Übungsreihenfolge, Ziel-Sätze, Wiederholungs-Spannen (z. B. 4× 8–12), Pausenzeiten, Supersatz-Gruppierung.
- **Übungsdatenbank (`/track/workouts/exercises`):** Interaktive SVG-Muskelkarte (`MuscleHeatmap2D`), Filter nach Equipment und Zielmuskel.
- **Live Active Session Mode (`/track/workouts/active`):**
  - Sticky Top Bar mit Live-Timer, Satz-Zähler und bewegter Tonnage.
  - Große Zifferntasten für Gewicht und Wiederholungen.
  - Vorherige Leistung der Vorwoche direkt als Referenz sichtbar.
  - Automatischer Pausen-Timer (`RestTimer.svelte`) mit Signalton/Vibration.
  - RPE-Schieberegler / Chips (1–10).

### 2.3 Ernährung & Food-Tracking (`/track/nutrition/*`)
- **Tages-Makro-Dashboard:** `MacroDonutGauge` (Kalorien, Protein, Kohlenhydrate, Fett) mit TDEE-Vergleich.
- **Mahlzeiten-Kategorien:** Frühstück, Mittagessen, Abendessen, Snacks, Pre/Post-Workout.
- **Lebensmittel-Suche:** Instant-Suche, Barcode-Scanner, Portions-Wähler (Gramm, Stück, Portion).
- **Rezept-Manager (`/track/nutrition/recipes`):** Zutaten kombinieren, automatische Makro-Berechnung pro Portion.

### 2.4 Fasten-Tracker (`/track/fasting`)
- **Visual Fasting Clock:** `FastingMetabolicClock.svelte` mit den 4 Stoffwechsel-Phasen (Glukose, Glykogen, Fettverbrennung/Ketose, Autophagie).
- **Protokolle:** 16:8, 18:6, 20:4, OMAD (23:1), Freies Fasten.
- **Historie:** Kalender-Heatmap der geführten Fastenperioden.

### 2.5 Gewohnheiten (Habits & Streaks) (`/track/habits/*`)
- **Tages-Checkliste:** Große Haptik-Buttons (`HabitCheckCircle.svelte`) mit SVG-Lichtburst.
- **Detailansicht (`/track/habits/[id]`):** 365-Tage GitHub-Style Jahresmatrix, Streak-Flammen, Habit-Stacking Notizen.

### 2.6 Klinische Labordaten (`/track/labs`)
- **Panel-Organisation:** Großes Blutbild, Fettstoffwechsel, Hormone & Schilddrüse, Stoffwechsel & Nieren, Vitamine.
- **Visuelle Referenz-Tachos:** `ClinicalGaugeMeter.svelte` mit 4 Zonen (`Niedrig`, `Optimal`, `Erhöht`, `Kritisch`) und Präzisions-Nadel.
- **Historische Zeitreihe:** Biomarker-Entwicklung über mehrere Bluttests hinweg.

### 2.7 Medikamente & Supplemente (`/track/medications/*`)
- **Tages-Dosis-Zeitplan:** Geordnete Einnahme-Karten nach Tageszeit (Morgens, Mittags, Abends, Nachts).
- **Next-Dose-Algorithmus:** Minutengenaue Ermittlung der nächsten fälligen Einnahme.
- **Inventar-Warnung:** Warn-Badge bei Unterschreiten des Mindestbestands.
- **Adhärenz-Statistik:** Monatliche Einnahme-Treuequote (%).

### 2.8 Mental Health (Mood & Journal) (`/track/mental/*`)
- **Stimmungs-Check-in:** 2D-Valenz-/Erregungs-Raster (`MoodValenceSphere.svelte`) mit optionalen Tags (*Fokus, Stress, Dankbarkeit*).
- **Journal:** Markdown-Editor mit Fokus-Modus, geführten Reflexionsfragen und Volltextsuche.

---

## 3. Säule 3: Insights & Intelligence (`/insights/*`)

### 3.1 Globale Trends & Korrelations-Matrix (`/insights/trends`)
- **Mathematischer Unterbau:** Berechnung von Pearson- ($r$) und Spearman-Korrelationen ($\rho$) zwischen zwei beliebigen Faktoren.
- **Verständliche Synthese:** Klartext-Aussagen wie *"Signifikanter Zusammenhang: An Tagen mit >8.000 Schritten schläfst du im Schnitt 34 Minuten länger."*

### 3.2 Zirkadianer Coach (`/insights/circadian`)
- **24h-Sonnenbogen (`CircadianSunArc.svelte`):** Dynamisch berechnet aus Aufwachzeit und Sonnenverlauf:
  - Licht-Exposition (erste 60 Min)
  - Kognitiver Peak (2–4h nach Aufwachen)
  - Koffein-Cutoff (8–10h vor dem Schlafen)
  - Melatonin- & Wind-Down Phase (90 Min vor dem Schlafen)

### 3.3 Forecast Lab (`/insights/forecast`)
- **Simulator:** Interaktiver Defizit-Schieberegler (-1000 bis +1000 kcal).
- **Wissenschaftliche Formel:** Projektion basierend auf $7.700\text{ kcal}/\text{kg}$ Fettgewebe und adaptivem TDEE über 30–180 Tage.

### 3.4 KI-Gesundheitscoach (Chat) (`/insights/coach`)
- Lokaler Chat-Assistent mit Zugriff auf die Dexie-Gesundheitsdaten unter Wahrung absoluter Privatsphäre.

### 3.5 Datenqualitäts-Inspektor (`/insights/data-quality`)
- Automatische Erkennung von Ausreißern (z. B. 800 kg statt 80.0 kg), doppelten Messungen und Zeitzonen-Fehlern mit 1-Klick-Reparatur.

---

## 4. Säule 4: Hub, Community & Settings (`/hub/*` & `/settings/*`)

### 4.1 Ziele, Meilensteine & Mathematische Prognosen (`/hub/goals`)
- **Regression & Konfidenzintervall:** `linearRegression` + `predictionInterval` für 80%-Konfidenztrichter bis zur Deadline.
- **Pace-Rechner:** Benötigte wöchentliche Veränderungsrate vs. aktuelle Geschwindigkeit.
- **Automatische Meilensteine:** 25%-, 50%-, 75%-Etappen.
- **Achievements:** Vektor-Medaillen mit Fortschrittsbalken.

### 4.2 E2EE-Freigaben & Datenexport (`/settings/shares` & `/settings/sources`)
- **Asymmetrische Arzt-Links:** Mit RSA/AES verschlüsselte Links mit Ablaufdatum und PIN.
- **Klinischer PDF-Bericht:** Druckfertiges Dokument für den Arztbesuch mit Vitalwerte-Verlauf und Labor-Tachos.
