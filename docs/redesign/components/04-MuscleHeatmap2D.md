# Komponentenspezifikation: `MuscleHeatmap2D.svelte`
**Pfad:** `frontend/src/lib/components/workouts/MuscleHeatmap2D.svelte`  
**Kategorie:** Organismus / Anatomische Visualisierung  
**Zweck:** Ästhetische, interaktive 2D-Vektor-Heatmap des menschlichen Körpers (Vorder- und Rückseite), die das akkumulierte Trainingsvolumen (kg) pro Muskelgruppe farbcodiert darstellt.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🏋️ MUSKEL-BELASTUNG (Letzte 7 Tage)           [ Front | Back ]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      (   Kopf   )                           │
│                     / [Schulter] \                          │
│                   /   [ Brust ]   \                         │
│                  | [B] [ Bauch ] [B]|                       │
│                  |     [Becken]    |                        │
│                   \   / Quad \   /                          │
│                    | [  rizeps] |                           │
│                    |  [Waden]   |                           │
│                                                             │
│   Farbskala:                                                │
│   [ Grau = 0 kg ]  [ Gelb = 1-3t ]  [ Koralle = 4-8t ] [ Rubin = >8t ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Anatomische Muskelgruppen & SVG-Pfade

Folgende Muskelgruppen sind als eigenständige, interaktive SVG-Pfade angelegt:

| Muskelgruppe | Code / Key | Ansicht |
|---|---|---|
| **Brust (Pectoralis)** | `chest` | Front |
| **Vordere & Seitliche Schulter (Deltoideus)** | `deltoids` | Front & Back |
| **Bizeps (Biceps brachii)** | `biceps` | Front |
| **Gerade & Schräge Bauchmuskeln (Abs / Obliques)** | `abs` | Front |
| **Quadrizeps (Quadriceps femoris)** | `quads` | Front |
| **Trapez & Nacken (Trapezius)** | `traps` | Back |
| **Breiter Rückenmuskel (Latissimus dorsi)** | `lats` | Back |
| **Unterer Rücken (Erector spinae)** | `lower_back` | Back |
| **Trizeps (Triceps brachii)** | `triceps` | Back |
| **Gesäßmuskel (Gluteus maximus)** | `glutes` | Back |
| **Beinbeuger (Hamstrings)** | `hamstrings` | Back |
| **Waden (Gastrocnemius / Soleus)** | `calves` | Front & Back |

---

## 3. Heatmap-Farbalgorithmus

Die Farbe jeder Muskelgruppe berechnet sich aus dem akkumulierten 7-Tage-Tonnage-Volumen ($V = \sum \text{weight} \times \text{reps}$) im Verhältnis zum optimalen Wochen-Zielvolumen ($V_{\text{target}}$):

$$\text{Intensity Ratio } R = \frac{V_{\text{actual}}}{V_{\text{target}}}$$

```typescript
function getMuscleColor(ratio: number): string {
  if (ratio === 0) return 'var(--color-surface-200)'; // Neutral Grau
  if (ratio < 0.5) return 'oklch(0.82 0.12 85)';      // Sanftes Gelb
  if (ratio < 1.0) return 'oklch(0.70 0.18 55)';      // Warmes Orange
  if (ratio <= 1.5) return 'oklch(0.62 0.20 48)';     // Sattes Korallenrot (Optimal)
  return 'oklch(0.52 0.22 25)';                       // Tiefes Rubin (Hohe Belastung)
}
```

---

## 4. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  volumeByMuscle: Record<string, number>; // z.B. { chest: 6400, lats: 8200, quads: 12000 }
  selectedMuscle?: string | null;
  interactive?: boolean; // Ermöglicht Klick auf Muskel zur Übungsfilterung
  onSelectMuscle?: (muscleKey: string) => void;
  size?: 'compact' | 'standard' | 'large';
}
```

---

## 5. Interaktives Verhalten

1. **Hover / Touch:** Beim Überfahren einer Muskelgruppe leuchtet diese mit einem dezenten Schimmer auf (`filter: drop-shadow(0 0 6px var(--color-primary))`). Ein schwebender Tooltip zeigt den Namen und das bewegte Volumen an (*"Brust: 6.400 kg (14 Sätze)"*).
2. **Klick / Selektion:** Ein Klick auf einen Muskel (z. B. *Latissimus*) filtert sofort die darunterliegende Übungsliste nach Rückenübungen oder öffnet die Übungshistorie.
3. **Ansichten-Toggle:** Ein eleganter `SegmentedControl` schaltet flüssig zwischen Vorder- und Rückseite um.
