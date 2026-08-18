# Salus 2.0 — Design-System & Token-Architektur
**Dokument:** `01-design-system.md`  
**Status:** Verbindlich

---

## 1. Farbsystem & Semantik (OKLCH)

Das Farbsystem basiert vollständig auf dem wahrnehmungsgerechten **OKLCH-Farbraum**, um absolut konsistente Helligkeitsabstufungen (Perceptual Uniformity) über alle Themes und Modi hinweg zu garantieren.

### 1.1 Domänenspezifische Farb-Tokens

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

---

## 2. Oberflächen- & Tiefen-Hierarchie (Surfaces & Elevation)

```
Ebene 0 (Hintergrund):    --color-surface-bg      oklch(0.985 0.002 260)  [Dark: oklch(0.13 0.01 260)]
Ebene 1 (Karten/Panel):   --color-surface-card    #ffffff                 [Dark: oklch(0.17 0.01 260)]
Ebene 2 (Innere Kacheln): --color-surface-subtle  oklch(0.965 0.004 260)  [Dark: oklch(0.21 0.01 260)]
Ebene 3 (Hover/Aktiv):    --color-surface-hover   oklch(0.935 0.006 260)  [Dark: oklch(0.26 0.01 260)]
Ebene 4 (Overlays/Sheets):--color-surface-overlay #ffffff (mit Blur)      [Dark: oklch(0.19 0.01 260)]
```

### Schatten-Tokens:
- **`shadow-card`**: `0 2px 10px -2px oklch(0 0 0 / 0.04), 0 1px 3px -1px oklch(0 0 0 / 0.02)`
- **`shadow-float`**: `0 12px 32px -4px oklch(0 0 0 / 0.08), 0 4px 12px -2px oklch(0 0 0 / 0.04)` (Sheets & FAB)
- **`shadow-glow-[color]`**: Subtiler Leuchtschein für aktive Zustände (z. B. aktives Workout oder Fasten).

---

## 3. Typografie-Maßstab (Manrope & Tabellenziffern)

- **Schriftart für UI & Text:** `Manrope`
- **Schriftart für Messwerte & Tabellen:** `font-variant-numeric: tabular-nums lining-nums`

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

---

## 4. Radien- & Spacing-Tokens

### Radien-Skala:
- `radius-sm`: `6px` (Badges, Tags, Indikatoren)
- `radius-md`: `10px` (Inputs, Buttons, Tab-Pills)
- `radius-lg`: `16px` (Standard-Karten, Widgets, Container)
- `radius-xl`: `24px` (Hero-Cards, Modals, Bottom Sheets)
- `radius-full`: `9999px` (Pillen, Progress-Ringe, Avatare)

### Spacing-Grid:
4px Basis (`space-1` = 4px, `space-2` = 8px, `space-3` = 12px, `space-4` = 16px, `space-6` = 24px, `space-8` = 32px, `space-12` = 48px).

---

## 5. Animationen & Transitions

- **Fast (Hover, Toggles):** `150ms cubic-bezier(0.4, 0, 0.2, 1)`
- **Normal (Accordion, Tab-Switch, Modals):** `250ms cubic-bezier(0.16, 1, 0.3, 1)`
- **Sheet / Page Transition:** `350ms cubic-bezier(0.32, 0.72, 0, 1)` (Flüssiges Spring/Decay).
- **Reduced Motion:** Automatische Reduktion aller Animationen auf `0.01ms` bei `prefers-reduced-motion: reduce`.

---

## 6. Barrierefreiheit & Farbfehlsichtigkeits-Modus

1. **Kontraste:** Alle Kern-Elemente und Texte erfüllen mindestens **WCAG AA (4.5:1)**.
2. **Farbfehlsichtigkeits-Modus (`data-colorblind="true"`):**  
   Verschiebung des Grün-Rot-Spektrums auf eine kontraststarke Blau-Bernstein-Achse (Rot = Signal-Rubin, Grün = Signal-Königsblau), sodass Protanopie, Deuteranopie und Tritanopie ohne Informationsverlust unterstützt werden.
