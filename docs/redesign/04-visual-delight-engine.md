# Salus 2.0 — Das Grafische Visualisierungs-System (*Visual Delight Engine*)
**Dokument:** `04-visual-delight-engine.md`  
**Status:** Verbindlich

---

## 1. Philosophie: Daten als lebendige Metaphern

Ein zentraler Pfeiler des Salus 2.0 Redesigns ist die Abkehr von reinen Text- und Zahlenlisten. Daten werden in **ästhetische, dynamisch animierte Vektorgrafiken und visuelle Metaphern** übersetzt, die sofort verständlich sind und Freude bei der Interaktion bereiten.

---

## 2. Die visuellen Vektor-Komponenten

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SALUS 2.0 VISUELLE GRAFIK-METAPHERN                                   │
├──────────────────────┬──────────────────────────────────────────┬──────────────────────────────────────┤
│ Domäne / Feature     │ Grafische Visualisierungs-Komponente     │ Visuelle Metapher & Interaktion      │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Hydration**        │ `HydrationWaveGlass.svelte`              │ Füllendes SVG-Glas mit animierten    │
│                      │                                          │ Wellen & aufsteigenden Bläschen      │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Fasten**           │ `FastingMetabolicClock.svelte`           │ Radialer Leuchtkreis mit 4 Zonen:    │
│                      │                                          │ Glukose, Ketose, Autophagie          │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Workouts**         │ `MuscleHeatmap2D.svelte`                 │ Anatomisches SVG-Körpermodell        │
│                      │                                          │ (Front/Back) mit 7-Tage-Volumen-Heat │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Zirkadian**        │ `CircadianSunArc.svelte`                 │ 24h-Sonnenbogen mit Live-Zeiger,     │
│                      │                                          │ kognitiven Peaks & Koffein-Cutoff    │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Schlaf**           │ `SleepHypnogram.svelte`                  │ Glatte Flächenkurve für Schlafzyklen │
│                      │                                          │ (Tief-, REM-, Leicht- & Wachschlaf)  │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Ernährung**        │ `MacroDonutGauge.svelte`                 │ Dreifach verschachtelte Glow-Ringe   │
│                      │                                          │ für Protein, Carbs, Fett + Kalorien  │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Labore**           │ `ClinicalGaugeMeter.svelte`              │ 4-Zonen-Tachometer mit Präzisions-   │
│                      │                                          │ Nadel und grünem Normalbereich       │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Mental / Mood**    │ `MoodValenceSphere.svelte`               │ 2D-Farbgradienten-Kugel, die sich    │
│                      │                                          │ nach Energie & Stimmung morpht       │
├──────────────────────┼──────────────────────────────────────────┼──────────────────────────────────────┤
│ **Widget-Galerie**   │ `WidgetGalleryCard.svelte`               │ Vollständig animierte Miniatur-Live- │
│                      │                                          │ Vorschau jedes Widgets vor dem Add   │
└──────────────────────┴──────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Detail-Spezifikation der Kernkomponenten

### 3.1 `HydrationWaveGlass.svelte` (Interaktives Wasserglas)
- **Visuelle Metapher:** Ein stilisiertes zylindrisches Trinkglas mit weicher Wölbung.
- **Flüssigkeits-Animation:** Zwei überlagerte SVG-Sinuskurven (`<path>`) oszillieren horizontal und vertikal mit sanfter Phasenverschiebung.
- **Interaktion:** Beim Erfassen neuer ml strömen kleine Bläschen nach oben; die Füllhöhe steigt mit elastischem Nachfedern (`spring()` Physik).

### 3.2 `FastingMetabolicClock.svelte` (Stoffwechsel-Uhr)
- **Visuelle Metapher:** 360°-Kreisdiagramm mit leuchtenden energetischen Abschnitten:
  - `0–4h`: Glukose-Verwertung (Blau)
  - `4–12h`: Glykogen-Abbau & Insulinsenke (Türkis)
  - `12–18h`: Fettverbrennung & Ketose (Bernstein/Gold)
  - `18–24h+`: Autophagie & Zellregeneration (Smaragd/Violett)
- **Live-Zeiger:** Ein pulsierender Leuchtpunkt wandert im Uhrzeigersinn entlang des Kreises und zeigt exakt an, in welcher Stoffwechselphase sich der Körper befindet.

### 3.3 `MuscleHeatmap2D.svelte` (Anatomische Muskel-Heatmap)
- **Visuelle Metapher:** Front- und Rückansicht des menschlichen Körpers als präzise SVG-Pfade.
- **Wärme-Gradient:** Jede Muskelgruppe (Brust, Rücken, Schultern, Arme, Beine, Rumpf) berechnet ihre Farbe aus dem Verhältnis von 7-Tage-Trainingsvolumen zu Zielvolumen:
  - 0% Volumen: Neutrales, dezentes Hellgrau (`surface-200`)
  - 50% Volumen: Warmes Gelb-Orange (`oklch(0.75 0.15 70)`)
  - 100% Volumen (Optimal): Sattes Korallenrot (`oklch(0.62 0.20 48)`)
  - >150% (Hohe Belastung): Tiefes Rubinrot mit Schimmer.

### 3.4 `SleepHypnogram.svelte` (Schlafphasen-Kurve)
- **Visuelle Metapher:** Sanfte Flächenkurve der Nacht:
  - Tiefschlaf (Dunkelindigo)
  - REM-Schlaf (Violett)
  - Leichtschlaf (Hellblau)
  - Wachphasen (Hellgrau/Amber)
- **Zyklus-Marker:** Automatische Hervorhebung von Schlafzyklen (~90-Minuten-Takte) und Schlafeffizienz.

### 3.5 `WidgetGalleryCard.svelte` (Live-Vorschau in der Widget-Galerie)
- Wenn der Nutzer das Dashboard anpassen möchte und den Widget-Katalog öffnet, sieht er **voll funktionsfähige Miniatur-Versionen** mit seinen echten Live-Daten.
- Er sieht vor dem Hinzufügen exakt, wie das Widget auf `Small`, `Medium` oder `Large` aussieht und reagiert.
