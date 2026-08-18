# Komponentenspezifikation: `CircadianSunArc.svelte`
**Pfad:** `frontend/src/lib/components/dashboard/CircadianSunArc.svelte`  
**Kategorie:** Organismus / Zirkadiane Rhythmus-Visualisierung  
**Zweck:** 24h-Sonnenbogen mit Live-Sonnen-/Mond-Positionierung, kognitiven Peak-Zonen, biologischem Lichtfenster, Koffein-Cutoff und Melatonin-Vorbereitungsphase.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ☀️ ZIRKADIANER TAGESRHYTHMUS                   [ 14:15 Uhr • Fokus-Phase ]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                     . - ~ ~ ~ ☀️ (14:15) ~ ~ ~ - .                          │
│                 . '                                ' .                      │
│               / [ 07:30 Licht ]         [ 14:30 Koffein-Cut ] \             │
│              |                                                 |            │
│            ──┴─────────────────────────────────────────────────┴──          │
│            06:00 (Aufwachen)                         22:30 (Schlafen)       │
│                                                                             │
│   Aktuelle Phase:                                                           │
│   🧠 KOGNITIVER PEAK (Noch 45 Min) • Nächster Schritt: ☕ Koffein-Stopp     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematische Phasen-Berechnung

Berechnet aus der individuellen Aufwachzeit ($T_{\text{wake}}$) und Ziel-Schlafenszeit ($T_{\text{bed}}$):

1. **Licht-Exposition ($T_{\text{wake}} \to T_{\text{wake}} + 60\text{m}$):** Natürliches Sonnenlicht zur Unterdrückung von Rest-Melatonin und Synchronisation der SCN-Master-Clock.
2. **Kognitiver Peak ($T_{\text{wake}} + 2\text{h} \to T_{\text{wake}} + 5\text{h}$):** Höchste Wachheit und Problemlösungskompetenz.
3. **Koffein-Cutoff ($T_{\text{bed}} - 9\text{h}$):** Exakte Deadline zur Vermeidung von Adenosin-Rezeptor-Blockaden im Tiefschlaf.
4. **Optimales Trainingsfenster ($T_{\text{wake}} + 9\text{h} \to T_{\text{wake}} + 12\text{h}$):** Maximale Körperkerntemperatur und Muskelkraft.
5. **Melatonin-Synthese & Wind-Down ($T_{\text{bed}} - 90\text{m}$):** Blaulicht minimieren, Raumtemperatur senken.

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  wakeTime: string; // z.B. "06:30"
  bedTime: string; // z.B. "22:30"
  currentTime?: string; // Standard: jetzt
  solarTimes?: { sunrise: string; solarNoon: string; sunset: string };
  size?: 'compact' | 'standard' | 'large';
}
```
