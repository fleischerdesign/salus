# Salus 2.0 — Datenvisualisierungs- & Chart-Standards
**Dokument:** `08-charts-and-data-viz.md`  
**Status:** Verbindlich

---

## 1. Grundsätze der Datenvisualisierung

Diagramme in Salus sind keine statischen Bilder, sondern **interaktive, wissenschaftliche Analysewerkzeuge**. Sie müssen gleichzeitig auf einen Blick Klarheit schaffen und bei Bedarf tiefgehende Rohdaten-Exploration ermöglichen.

---

## 2. Standardisierte Zeitachsen

Alle Charts in Salus unterstützen einheitliche Zeit-Intervalle:

```
┌───────────┬─────────────────────────┬────────────────────────────────────────────────────────┐
│ Intervall │ Abdeckung               │ X-Achsen-Beschriftung                                  │
├───────────┼─────────────────────────┼────────────────────────────────────────────────────────┤
│ **7D**    │ Letzte 7 Tage           │ Wochentage (`Mo, Di, Mi, Do, Fr, Sa, So`)             │
│ **30D**   │ Letzte 30 Tage          │ Datumsstempel im 5-Tage-Takt (`1. Aug, 6. Aug...`)     │
│ **90D**   │ Letztes Quartal (3 Mon.)│ Monatstage / Kalenderwochen                            │
│ **1Y**    │ Letztes Jahr (12 Mon.)  │ Monatsnamen (`Jan, Feb, Mär, Apr...`)                  │
│ **ALL**   │ Komplette Historie      │ Jahreszahlen & Quartale                                │
└───────────┴─────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Rauschunterdrückung & 7-Tage-EMA (Exponential Moving Average)

Gerade bei Messwerten, die durch Wasserhaushalt oder Tageszeit stark schwanken (z. B. Körpergewicht, Ruhepuls oder Blutdruck), blendet Salus standardmäßig zwei Kurven ein:
1. **Rohwert-Punkte / Dünne Spline-Linie:** Zeigt die echten Tagesmessungen.
2. **7-Tage-EMA-Linie (Gleitender Durchschnitt):** Beruhigte Trendlinie, die kurzfristige Ausreißer filtert und den wahren biologischen Trend sichtbar macht.

---

## 4. Zielkorridore & Konfidenzbänder

- **Klinische & Ziel-Korridore:**
  - Optimale Bereiche (z. B. Blutdruck $110-120 / 70-80\text{ mmHg}$) werden als sanft schattierte, halbtransparente Hintergrundbänder hinterlegt (`rgba(green, 0.08)`).
- **Prognose-Trichter:**
  - Bei Ziel-Projektionen (z. B. Gewichtsverlust bis zu einer Deadline) wird das 80%-Konfidenzintervall als sich auffächernder Lichttrichter dargestellt.

---

## 5. Interaktion: Tooltip-Scrubbing & Zoom

- **Scrubbing (Desktop & Touch):**
  - Horizontales Wischen oder Bewegen der Maus erzeugt eine feine vertikale Haarlinie mit magnetischem Einrasten am nächsten Messpunkt.
- **Floating Tooltip (Glasmorphismus):**
  - Zeigt exaktes Datum und Uhrzeit.
  - Messwert mit Einheit und Abweichung zum 7-Tage-Schnitt (*"78.4 kg • ↘ -0.3 kg"*).
  - Optionaler Kontext: Wurde an diesem Tag ein Training absolviert oder ein Fasten abgeschlossen?
- **Pinch-to-Zoom (Touch) & Mausrad:**
  - Flüssiges Hinein- und Herauszoomen in hochfrequente Daten (z. B. HRV-Verlauf über die Nacht).
