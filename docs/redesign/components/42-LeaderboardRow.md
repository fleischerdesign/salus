# Komponentenspezifikation: `LeaderboardRow.svelte`
**Pfad:** `frontend/src/lib/components/community/LeaderboardRow.svelte`  
**Kategorie:** Molekül / Ranglisten-Zeile  
**Zweck:** Anonymisierte, datenschutzkonforme Community-Ranglisten-Zeile für Gruppen-Challenges (z.B. Schritte, Wasser, Fastenstunden) mit Rang-Medaillen, Pseudonym und relativem Fortschrittsbalken.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 🥇 #1  [ Avatar ] @MetabolicPro          🔥 28T  14.280 Schritte│
│ ██████████████████████████████████████████████████ [ 100% ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  rank: number;
  displayName: string;
  avatarSeed?: string;
  scoreValue: number;
  unit: string;
  maxScore: number;
  streakDays?: number;
  isCurrentUser?: boolean;
}
```
