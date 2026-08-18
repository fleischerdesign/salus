# Komponentenspezifikation: `HeroProgressRings.svelte`
**Pfad:** `frontend/src/lib/components/dashboard/HeroProgressRings.svelte`  
**Kategorie:** Organismus / Visueller Hero-Tagesstatus  
**Zweck:** 3 konzentrische, ineinander verschachtelte SVG-Fortschrittsringe für die zentralen Säulen des Tages (Aktivität/Schritte, Hydration/Wasser, Habits/Gewohnheiten) mit flüssigen Glow-Verläufen.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ( ( (  84%  ) ) )                                │
│                                                                             │
│                    Äußerer Ring:   🚶 Aktivität (8.420 / 10.000 Schritte)   │
│                    Mittlerer Ring: 💧 Hydration (2.250 / 3.000 ml)          │
│                    Innerer Ring:   🔥 Habits (3 / 4 erledigt)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Geometrie & SVG-Mathematik

3 konzentrische Kreisbahnen mit dezentem Hintergrund-Track (`stroke="rgba(var(--color), 0.15)"`) und dynamischem Vordergrund-Strich:

```typescript
const RINGS = [
  { id: 'activity', radius: 88, strokeWidth: 14, color: 'var(--color-activity)' },
  { id: 'hydration', radius: 70, strokeWidth: 14, color: 'var(--color-hydrate)' },
  { id: 'habits', radius: 52, strokeWidth: 14, color: 'var(--color-circadian)' }
];
```

- **Umfang:** $C_i = 2 \pi r_i$
- **Dashoffset:** $\text{offset}_i = C_i \times (1 - \min(\text{percent}_i / 100, 1))$
- **Linienenden:** `stroke-linecap="round"` mit leichtem Glow-Filter am Zeigerende (`filter: drop-shadow(0 0 6px var(--ring-color))`).

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  activity: { current: number; target: number; percent: number; label: string };
  hydration: { current: number; target: number; percent: number; label: string };
  habits: { current: number; target: number; percent: number; label: string };
  size?: number; // z.B. 240px
}
```
