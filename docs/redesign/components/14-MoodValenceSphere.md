# Komponentenspezifikation: `MoodValenceSphere.svelte`
**Pfad:** `frontend/src/lib/components/mood/MoodValenceSphere.svelte`  
**Kategorie:** Organismus / Emotionale 2D-Visualisierung  
**Zweck:** Ästhetische, interaktive 2D-Farbgradienten-Kugel auf einer Valenz- (Stimmung) und Erregungs-Achse (Energie/Fokus) mit haptischem Feedback.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 😊 STIMMUNG & ENERGIE                             [ 1-Tap Pick ]│
├─────────────────────────────────────────────────────────────┤
│                    HOHE ENERGIE                             │
│                         ▲                                   │
│           ( Gestresst ) │ ( Euphorie / Flow )               │
│                         │                                   │
│  NEGATIV ───────────────● (Ausgeglichen) ────── POSITIV     │
│                         │                                   │
│           ( Erschöpft ) │ ( Gelassen / Ruhig )              │
│                         ▼                                   │
│                   NIEDRIGE ENERGIE                          │
│                                                             │
│   Aktuell gewählt: 🟢 4/5 (Motiviert & Ausgeglichen)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  score?: number; // 1 bis 5 (oder 2D x, y)
  energyLevel?: number; // 1 bis 5
  interactive?: boolean;
  onSelect?: (score: number, energy: number) => void;
  size?: 'compact' | 'standard' | 'large';
}
```
