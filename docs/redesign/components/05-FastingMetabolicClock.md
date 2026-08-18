# Komponentenspezifikation: `FastingMetabolicClock.svelte`
**Pfad:** `frontend/src/lib/components/fasting/FastingMetabolicClock.svelte`  
**Kategorie:** Organismus / Radialer Stoffwechsel-Timer  
**Zweck:** Visualisierung der aktuellen Fastenperiode mit Kreis-Zeiger, verbleibender Restzeit und genauer Anzeige der erreichten metabolischen Phase (Glukose, Ketose, Autophagie).

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ ⏳ FASTEN-STATUS (16:8 Protokoll)               [ Ziel: 12:30 ]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                      (   14h 32m   )                        │
│                   /   /           \   \                     │
│                  |   |  Noch 1h 28m|   |                    │
│                  |   |    bis 16h  |   |                    │
│                   \   \           /   /                     │
│                      (  FETTVERBRENNUNG  )                  │
│                                                             │
│   Stoffwechsel-Phasen:                                      │
│   [ 0-4h Blutzucker ]  [ 4-12h Glykogen ]  [ 12-18h Ketose ] [ 18-24h+ Autophagie ]│
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Die 4 Metabolischen Zonen & Farbskalen

| Phase | Zeitfenster | Farbton / Token | Physiologischer Zustand |
|---|---|---|---|
| **Phase 1** | `0 – 4 Stunden` | Blassblau (`oklch(0.75 0.10 220)`) | **Blutzucker-Stabilisierung:** Insulin sinkt, Magen-Darm-Trakt leert sich. |
| **Phase 2** | `4 – 12 Stunden` | Türkis (`oklch(0.68 0.15 190)`) | **Glykogen-Entleerung:** Leber-Glykogenspeicher werden zur Energiegewinnung abgebaut. |
| **Phase 3** | `12 – 18 Stunden` | Bernstein / Gold (`oklch(0.70 0.18 70)`) | **Fettverbrennung & Ketose:** Beta-Oxidation steigt massiv an, Ketonkörper (BHB) steigen im Blut. |
| **Phase 4** | `18 – 24+ Stunden` | Smaragd / Violett (`oklch(0.60 0.20 150)`) | **Autophagie & Zellerneuerung:** Zelluläre Müllabfuhr, Seneszenzzell-Abbau. |

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  startedAt: string; // ISO Timestamp
  targetHours: number; // z.B. 16
  endedAt?: string | null; // Falls Session beendet
  waterOnly?: boolean;
  onEnd?: () => Promise<void> | void;
  onCancel?: () => Promise<void> | void;
  size?: 'compact' | 'standard' | 'large';
}
```

---

## 4. Reaktivität & Timer-Logik

1. **Echtzeit-Ticker:** Ein `$effect`-gestützter 10-Sekunden-Intervall aktualisiert die abgelaufene Zeit (`elapsedHours`) präzise gegen `Date.now()`.
2. **SVG-Kreisbogen-Mathematik:**
   - Radius $r = 100\text{px}$, Umfang $C = 2\pi r \approx 628.32\text{px}$.
   - `stroke-dasharray = C`, `stroke-dashoffset = C * (1 - Math.min(elapsedHours / targetHours, 1))`.
   - Bei Überziehen des Ziels ($>100\%$) wechselt der Kreis in einen sanft pulsierenden goldenen Überziehungs-Modus.
