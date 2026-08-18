# Salus 2.0 — Schrittweiser Migrations- & Implementierungsplan
**Dokument:** `10-implementation-roadmap.md`  
**Status:** Verbindlich

---

## 1. Phasen-Architektur

Die Umsetzung erfolgt in **4 strikt voneinander abgegrenzten Phasen**, um jederzeitige Lauffähigkeit, Null Ausfallzeiten und Zero-Regression zu garantieren.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                       FAHRPLAN FÜR DAS REDESIGN (SALUS 2.0)                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: Design-Fundament & Globale Shell                                               │
│ • app.css Design-Tokens (OKLCH-Farben, Radien, Shadows, Typo-Scale)                     │
│ • Neue Navigation: TopAppBar.svelte (Desktop) & BottomNavBar.svelte (Mobile)            │
│ • Universal QuickLogSheet.svelte & Tastatur-Shortcut (Taste L / FAB)                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 2: Das "Heute" Cockpit (Dashboard)                                                │
│ • Hero-Header mit Begrüßung, Datum-Navigation & Tages-Puls Ringe                       │
│ • Chronologische Zirkadian- & Tages-Timeline                                            │
│ • Überarbeitung der interaktiven Widget-Kacheln (Wasser, Fasten, Schritte, Habits)      │
│ • Visueller Widget-Katalog Drawer mit animierten Miniatur-Live-Vorschauen               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: Track & Body Zentrale (/track/*)                                               │
│ • Zusammenführung von Metriken, Workouts, Food, Fasten, Habits und Labs unter /track    │
│ • Live Workout Active Mode mit MuscleHeatmap2D & Rest-Timer                             │
│ • Food & Recipe Manager mit visuellen MacroDonutGauges                                  │
│ • ClinicalGaugeMeter für klinische Blutwerte & Referenzbereiche                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 4: Insights, Community & Polishing                                                │
│ • CircadianSunArc & Korrelations-Matrix Redesign                                        │
│ • Forecast Lab & KI-Coach UI                                                            │
│ • Gesten (Swipe-to-Complete, Tag-Wischen) & haptisches Feedback                         │
│ • Klinischer PDF-Gesundheitsbericht für Ärzte                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detaillierte Arbeitspakete pro Phase

### Phase 1: Design-Fundament & Globale Shell
1. **Design Tokens:** `app.css` aktualisieren mit OKLCH-Skalen für alle Domänen, neuen Schattierungen (`shadow-card`, `shadow-float`), Radien (`rounded-2xl`).
2. **Atomic UI-Atome:** `Btn.svelte`, `Card.svelte`, `Input.svelte`, `SegmentedControl.svelte`, `Badge.svelte` überarbeiten.
3. **Responsive Shell:** `TopAppBar.svelte` auf die 4 Hauptsäulen reduzieren, `BottomNavBar.svelte` für Mobile PWA integrieren.
4. **Quick-Log:** `QuickLogSheet.svelte` implementieren mit globalem Trigger (Taste `L`, Button `+`).

### Phase 2: Das "Heute" Cockpit (Dashboard)
1. **Hero & Pulse Ringe:** `HeroProgressRings.svelte` für Aktivität, Wasser, Habits.
2. **Timeline:** Chronologische Zirkadian- und Tageszeitleiste.
3. **Widgets:** `HydrationWaveGlass.svelte`, `FastingMetabolicClock.svelte`, Kacheln modernisieren.
4. **Widget-Galerie:** `WidgetGalleryCard.svelte` mit Live-Miniaturvorschauen im Add-Drawer.

### Phase 3: Track & Body Zentrale (`/track/*`)
1. **Routing & Hub:** `/track` Hauptübersicht und Redirects bestehender Routen.
2. **Workout Live Mode:** Große Touchpads, automatische Pausen, RPE-Chips, `MuscleHeatmap2D.svelte`.
3. **Ernährung:** `MacroDonutGauge.svelte`, Barcode-Scan, Rezept-Makroberechnung.
4. **Labore & Meds:** `ClinicalGaugeMeter.svelte`, Einnahme-Zeitplan und Inventar-Warnungen.

### Phase 4: Insights, Community & Polishing
1. **Statistik-Zentrale:** Korrelationsmatrix mit Pearson/Spearman und Klartextsynthese.
2. **Zirkadian-Uhr:** `CircadianSunArc.svelte` mit Tageslicht- und Melatonin-Fenstern.
3. **Klinischer PDF-Export:** High-Res PDF-Generator für Arztberichte.
4. **Gesten & Haptik:** Wischgesten für Tageswechsel und Habit-Completion.
