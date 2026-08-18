# Salus 2.0 — Testing & Quality Assurance (QA) Strategie
**Dokument:** `24-testing-and-quality-assurance-strategy.md`  
**Status:** Verbindlich  
**Zweck:** Ganzheitliche Test-Strategie mit mathematischer Validierung, Vitest Komponenten-Tests, Playwright E2E-Tests und visueller Regressionsprüfung.

---

## 1. Die Test-Pyramide von Salus 2.0

```
                   / \
                  /   \
                 / E2E \       Playwright (Offline, E2EE Share, Workout Flow)
                /───────\
               /  Visual \     Playwright Screenshots (Dark, Light, Colorblind)
              /───────────\
             /  Komponenten\   Vitest + @testing-library/svelte (86 Komponenten)
            /───────────────\
           / Mathematisch /  \ Vitest / Pytest (r, rho, EMA, 1RM, Konvertierungen)
          /───────────────────\
```

---

## 2. Mathematische Verifikations-Tests (Zero Float Inaccuracy)

Alle statistischen und biomechanischen Formeln werden gegen bekannte Referenz-Datensätze getestet:

```typescript
// tests/math.test.ts
import { describe, it, expect } from 'vitest';
import { calculateEMA, calculate1RM, pearsonCorrelation } from '$lib/utils/math';

describe('Mathematische Korrektheit', () => {
  it('berechnet 1RM nach Brzycki exakt', () => {
    // 100kg für 5 Wdh: 100 / (1.0278 - (0.0278 * 5)) = 112.51 kg
    expect(calculate1RM(100, 5)).toBeCloseTo(112.51, 1);
  });

  it('berechnet 7-Tage EMA glatt und phasenkorrekt', () => {
    const data = [70, 71, 70, 72, 73, 72, 71];
    const ema = calculateEMA(data, 7);
    expect(ema[ema.length - 1]).toBeCloseTo(71.4, 1);
  });
});
```

---

## 3. Playwright E2E & Visuelle Regression

1. **Offline Flow:** Trennen der Netzwerkverbindung (`page.context().setOffline(true)`), Eintragen von Blutdruck & Workout, Wiederherstellen der Verbindung -> Verifikation, dass die Outbox automatisch geleert wird und SSE synchronisiert.
2. **Visuelle Screenshots:** Pixelgenauer Vergleich von Diagrammen, Kacheln und Modals auf Desktop (1440px), Tablet (768px) und Smartphone (375px).
