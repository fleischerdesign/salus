# Komponentenspezifikation: `EmptyState.svelte`
**Pfad:** `frontend/src/lib/components/ui/EmptyState.svelte`  
**Kategorie:** Molekül / Motivierender Leerzustand  
**Zweck:** Ästhetischer, freundlicher und motivierender leerer Zustand mit thematischer Vektor-Illustration, klarer Hilfestellung und direktem Call-to-Action (CTA).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      [ 📊 SVG-Grafik ]                      │
│                                                             │
│                 Noch keine Workouts erfasst                 │
│   Starte dein erstes Training oder wähle einen Split-Plan,   │
│   um deine Muskel-Heatmap und Kraftkurven aufzubauen.       │
│                                                             │
│                  [ + Erstes Workout starten ]               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  icon?: string; // Material Symbols Icon
  illustration?: 'workouts' | 'nutrition' | 'fasting' | 'labs' | 'habits' | 'metrics';
  title: string;
  description: string;
  actionLabel?: string;
  actionIcon?: string;
  onaction?: () => void;
}
```
