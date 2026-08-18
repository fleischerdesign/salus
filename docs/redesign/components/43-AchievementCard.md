# Komponentenspezifikation: `AchievementCard.svelte`
**Pfad:** `frontend/src/lib/components/hub/AchievementCard.svelte`  
**Kategorie:** Molekül / Trophäen- & Meilenstein-Karte  
**Zweck:** Interaktive Trophäen-Karte mit subtilem 3D-Kippeffekt bei Hover (`perspective: 1000px`), Rangstufen (Bronze, Silber, Gold, Platin), Fortschrittsbalken und Freischaltdatum.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│                      [ 🏆 GOLD-MEDAILLE ]                   │
│                       METABOLISCHER MEISTER                 │
│              Absolviere 30 erfolgreiche Fasten-Sessions      │
│                                                             │
│   Fortschritt: 28 / 30 Fasten-Tage (93%)                    │
│   ██████████████████████████████████████████░░░░            │
│                                                             │
│   [ Noch 2 Tage bis zum Platin-Upgrade! ]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  title: string;
  description: string;
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  currentProgress: number;
  targetProgress: number;
  unlockedAt?: string | null;
  icon?: string;
}
```
