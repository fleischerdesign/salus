# 02 — Informationsarchitektur & Tri-Modales Navigationssystem (Salus 2.0)

Salus 2.0 bricht radikal mit veralteten, platzverschwendenden 250px-Admin-Seitenleisten der 2010er Jahre. Stattdessen setzt Salus auf das **Tri-Modale Dynamic Navigation System**: Eine ultra-moderne, schwebende Glasmorphismus-Dock-Architektur, die auf Desktop-Bildschirmen volle 100 % Canvas-Breite für Daten bietet und auf Smartphones automatisch in die ergonomische Daumen-Zone gleitet.

---

## 1. Die drei Säulen der Tri-Modalen Navigation

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│               DIE MODERNE 3-STUFIGE TRI-MODAL NAVIGATION (SPATIAL DOCK + FLYOUT DECKS)                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. DAS SCHWEBENDE CONTEXTUAL GLASS-DOCK (Center Stage)                                                │
│    • Desktop: Oben zentriert schwebend im Blickfeld mit `backdrop-filter: blur(24px)`.                 │
│    • Mobile / PWA: Gleitet automatisch an den unteren Bildschirmrand in die ergonomische Daumen-Zone.  │
│    • Bündelt die 4 Haupt-Kontexte: [ ☀️ Heute ] [ 📊 Track ▾ ] [ 🧬 Klinik ▾ ] [ 🧠 Insights ]         │
│                                                                                                        │
│ 2. GLANCEABLE FLYOUT SUB-DECKS & MOBILE BOTTOM-SHEETS (Mega-HUD)                                       │
│    • Klick auf `Track` oder `Klinik` öffnet ein schwebendes Sub-Deck mit Live-Status-Zusammenfassung:  │
│      - Desktop: Schwebt sanft nach unten auf (`deckPop 0.2s cubic-bezier`).                            │
│      - Mobile: Fährt als taktiles Bottom-Sheet von unten nach oben (`sheetSlideUp 0.3s cubic-bezier`). │
│      - Zeigt Live-Zustand (z. B. "Push Day A bereit", "Noch 560 kcal", "LDL 68 mg/dL") vor dem Sprung.│
│                                                                                                        │
│ 3. ZERO-CLICK OMNI-COMMAND ENGINE (`Cmd+K` Spotlight)                                                 │
│    • Schneller Tastatur-Zugriff auf alle 31 Routen (`G W` = Workouts, `G L` = Labore, `G F` = Food).   │
│    • Taktiler 1-Tap Quick-Log über Taste `L` oder den Action Orb im Dock.                             │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Die 4 Primären Kontext-Säulen (Pillars)

Jede Säule deckt einen fundamentalen mentalen Zustand des Nutzers ab:

### Säule 1: ☀️ Heute (Daily Cockpit & Vital Pulse)
- **Mentaler Fokus:** *"Wo stehe ich heute zu diesem Zeitpunkt?"*
- **Kern-Elemente:**
  - Astronomische 24h-Sonnenbahn (`CircadianSunArc`) mit aktuellem Sonnenstand, kognitivem Peak und Koffein-Cutoff.
  - Sinus-Wellenglas (`HydrationWaveGlass`) für Wasserhaushalt.
  - 360° Stoffwechsel-Fastenuhr (`FastingMetabolicClock`) mit Autophagie-/Ketose-Zonen.
  - 4-Zonen Blutdruck-Tachometer (`ClinicalGaugeMeter`) nach ESC/EAS 2024.
  - 52-Wochen Habit-Konsistenz-Matrix im GitHub-Stil.

### Säule 2: 📊 Track & Log (Aktive Erfassung & Training)
- **Mentaler Fokus:** *"Ich führe gerade eine Aktivität aus oder protokolliere Daten."*
- **Sub-Domänen im Flyout-Deck:**
  - **Workouts & Splits (`/workouts`):** Live-Training Focus Screen mit Satz-Logger, Countdown-Pausentimer (`+30s`) und 2D-Muskel-Heatmap.
  - **1RM Kraftmodelle (`/workouts/exercises`):** Brzycki-Kraftkurven und persönliche Rekorde.
  - **Ernährungstagebuch (`/food`):** Mahlzeiten (Frühstück, Mittag, Abend) mit Makro-Zutaten und Kalorien-Budget.
  - **Rezept-Katalog (`/recipes`):** Skalierbare Rezepte & Meal-Prep Vorlagen.
  - **Intervallfasten (`/fasting`):** Protokollierte Fasten-Sessions & Zonen.
  - **Gewohnheiten & Habits (`/habits`):** Tägliche Check-ins & Streak-Tracker.
  - **Journal & Mental (`/journal`):** Zen-Modus Reflexion & geführte Prompts.

### Säule 3: 🧬 Klinik & Labore (Medizin & Evidenz)
- **Mentaler Fokus:** *"Ärztliche Befunde, Biomarker-Zeitreihen und Medikation."*
- **Sub-Domänen im Flyout-Deck:**
  - **Biomarker-Verlaufsmatrix (`/labs`):** Multi-Draw Zeitreihen mit Live-Umschaltung zwischen `mg/dL` und `mmol/L`.
  - **Medikationsplan & Vorrat (`/medications`):** Einnahme-Schedules, Bestands-Tracker und PDC-Adhärenz.
  - **Kardiovaskuläres Profil (`/entries/blood_pressure`):** Langzeit-Blutdruckkurven & 7-Tage-EMAs.
  - **Zero-Knowledge E2EE Arzt-Freigaben (`/settings/shares`):** WebCrypto AES-GCM 256-Bit Link-Generator mit PIN-Schutz.
  - **Arztbrief-Export:** DIN/ISO-konformer PDF-Export für den Facharzt.

### Säule 4: 🧠 Insights & Analytik (Wissenschaft & Ziele)
- **Mentaler Fokus:** *"Welche Muster und Zusammenhänge leiten sich aus meinen Daten ab?"*
- **Sub-Domänen:**
  - **Korrelationsmatrix (`/analytics`):** Automatisierte Pearson $r$ und Spearman $\rho$ Korrelationen (z. B. Schlaf ↔ Blutdruck $r = -0.74^*$, Protein ↔ Kraft $r = +0.81^*$).
  - **Trend-Splines:** 30-Tage Glättungskurven mit 80 % Konfidenzbändern.
  - **Ziele & Korridore (`/goals`):** Mathematische Zielprojektionen und Pacing-Rechner.
  - **Trophäen & Meilensteine (`/achievements`):** 3D-Tilt Trophäen-Karten mit Rang-Stufen (Gold, Platin, Diamant).

---

## 3. Responsive Adaptive Architecture (Desktop vs. Mobile)

```
DESKTOP VIEWPORT (>= 769px)               MOBILE PWA VIEWPORT (<= 768px)
┌──────────────────────────────────────┐  ┌───────────────────────────────────┐
│     [  ☀️ Heute  📊 Track ▾  ...  ]  │  │  (Notch / Dynamic Island)        │
│                                      │  │                                   │
│  [ Card 1 ]  [ Card 2 ]  [ Card 3 ]  │  │  [ Full-Width Card 1 ]            │
│                                      │  │                                   │
│  [ Table / Wide Chart (100% Width) ] │  │  [ Full-Width Card 2 ]            │
│                                      │  │                                   │
│                                      │  │  [ Horizontally Swiping Table ]   │
│                                      │  │                                   │
│                                      │  │  ┌─────────────────────────────┐  │
│                                      │  │  │ [Heute] [Track] [Klinik] [+]│  │
└──────────────────────────────────────┘  └──┴─────────────────────────────┴──┘
                                             ▲ Daumen-Zone am unteren Rand
```

### Mobile PWA Besonderheiten:
1. **Ergonomic Thumb Anchoring:** Das Dock sitzt am unteren Rand (`bottom: calc(16px + env(safe-area-inset-bottom))`). Alle primären Aktionen sind mit einer Hand ohne Umgreifen erreichbar.
2. **Bottom-Sheet Flyouts:** Beim Antippen von `Track` oder `Klinik` gleitet ein elegantes Bottom-Sheet-Modal von unten ins Bild (`sheetSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)`), das durch Wischen nach unten geschlossen werden kann.
3. **Scroll-Containment & Zero Collisions:** Der Hauptinhalt besitzt `padding-bottom: 100px`, wodurch das letzte Element immer frei über dem Dock sichtbar bleibt.
4. **Horizontale Wisch-Container (`.table-wrap`):** Tabellen mit mehreren Messzeitpunkten brechen nicht um, sondern lassen sich horizontal butterweich mit dem Daumen scrollen (`overflow-x: auto; -webkit-overflow-scrolling: touch`).

---

## 4. Tastatur- und Barrierefreiheits-Engine

| Shortcut | Aktion | Verhalten |
|---|---|---|
| `Cmd + K` / `Strg + K` | Spotlight-Palette öffnen | Fuzzy-Suche über alle 31 Unterseiten, Metriken und Aktionen |
| `L` | 1-Tap Schnell-Logging | Öffnet das taktile Ziffernblock-Modal |
| `Escape` | Modal / Deck schließen | Schließt geöffnete Decks, Sheets und Dialoge |
| `Tab` / `Shift + Tab` | Fokus-Navigation | Sichtbarer, doppelter Fokus-Ring nach WCAG 2.2 AAA |
| `1` bis `4` | Pillar-Direktsprung | 1 = Heute, 2 = Track, 3 = Klinik, 4 = Insights |
