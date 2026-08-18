# Komponentenspezifikation: `MethodologyBadge.svelte`
**Pfad:** `frontend/src/lib/components/ui/MethodologyBadge.svelte`  
**Kategorie:** Atom / Wissenschaftliches Transparenz-Popover  
**Zweck:** Dezent platziertes Info-Badge `[ ℹ️ Methodik ]`, das sich bei Klick als Popover öffnet und behandelnden Ärzten, Wissenschaftlern und Nutzern die exakten mathematischen Formeln, $p$-Werte, Stichprobengrößen und Referenzquellen offenlegt.

---

## 1. Visuelle Spezifikation

```
[ ℹ️ Methodik ] ➔ (Öffnet Popover)
┌─────────────────────────────────────────────────────────────┐
│ WISSENSCHAFTLICHE METHODIK & FORMEL                         │
├─────────────────────────────────────────────────────────────┤
│ • Berechnungsformel: Pearson-Produkt-Moment-Korrelation     │
│   r = Σ((x - x̄)(y - ȳ)) / sqrt(Σ(x - x̄)² * Σ(y - ȳ)²)      │
│ • Stichprobe (n): 90 Tage (01.06.2026 – 31.08.2026)         │
│ • Freiheitsgrade (df): 88                                   │
│ • Statistische Signifikanz: p = 0.0004 (Hochsignifikant)    │
│ • Quelle / Leitlinie: American Heart Association (AHA 2024) │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  formulaName: string;
  formulaLatex?: string;
  sampleSizeN?: number;
  pValue?: number;
  rSquared?: number;
  guidelineSource?: string;
  description?: string;
}
```
