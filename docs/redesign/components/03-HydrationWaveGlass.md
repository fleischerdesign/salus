# Komponentenspezifikation: `HydrationWaveGlass.svelte`
**Pfad:** `frontend/src/lib/components/food/HydrationWaveGlass.svelte`  
**Kategorie:** Organismus / Visuelle Metapher  
**Zweck:** Lebendige, dynamisch animierte Darstellung des täglichen Wasserhaushalts mit füllendem SVG-Glas, oszillierenden Sinuswellen und 1-Tap Schnell-Buttons.

---

## 1. Visuelle Spezifikation

```
┌─────────────────────────────────────────────────────────────┐
│ 💧 HYDRATION                                     75% ZIEL   │
├─────────────────────────────────────────────────────────────┤
│                 ┌───────────────────────┐                   │
│                 │ \                   / │                   │
│                 │  \                 /  │                   │
│                 │   \ ~~~~~~~~~~~~~ /   │  2.250 ml         │
│                 │    \ ~ ~ ~ ~ ~ ~ /    │  / 3.000 ml       │
│                 │     \ ~ ~ ~ ~ ~ /     │                   │
│                 │      \_________/      │                   │
│                 └───────────────────────┘                   │
│                                                             │
│       [ +250 ml Glas ]           [ +500 ml Flasche ]        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematische & SVG-Animation

### 2.1 Oszillierende Sinuswellen-Mathematik
Zwei gegenläufige Sinuskurven erzeugen einen realistischen Flüssigkeitseffekt:

$$y_1(x, t) = A \cdot \sin\left(\frac{2\pi}{\lambda} \cdot x + \omega \cdot t\right) + y_{\text{fill}}$$
$$y_2(x, t) = A \cdot \sin\left(\frac{2\pi}{\lambda} \cdot x - \omega \cdot t + \phi\right) + y_{\text{fill}}$$

- **Amplitude ($A$):** $6\text{px}$ (subtile, beruhigende Welle).
- **Wellenlänge ($\lambda$):** $180\text{px}$ (passend zur Glasbreite).
- **Füllhöhe ($y_{\text{fill}}$):** Berechnet aus $\text{currentMl} / \text{targetMl} \times \text{Glashöhe}$.
- **Farbverlauf:** Sattes Türkis-Cyan (`oklch(0.68 0.16 210)`) oben bis zu tiefem Ozeanblau (`oklch(0.55 0.18 230)`) am Glasboden.

---

## 3. Props & Schnittstellen (Svelte 5 Runes)

```typescript
interface Props {
  currentMl: number;
  targetMl: number;
  onAdd?: (amountMl: number) => Promise<void> | void;
  size?: 'compact' | 'standard' | 'large';
  showQuickButtons?: boolean;
}
```

---

## 4. Interaktion & Mikro-Animationen

1. **Flüssiges Auffüllen (`spring()`):**
   - Wird Wasser hinzugefügt (z.B. `+250ml`), steigt der Wasserspiegel nicht abrupt, sondern federt mit Svelte-Spring-Physik (`stiffness: 0.15, damping: 0.8`) sanft nach oben.
2. **Aufsteigende Partikel/Bläschen:**
   - Bei jedem Klick auf einen Schnell-Button werden 4–6 kleine SVG-Kreise animiert vom Boden an die Oberfläche gespült und platzen mit einem dezenten Skalierungs-Effekt (`scale: 0 -> 1.2 -> 0`).
3. **Erfolgs-Zustand (100% Ziel erreicht):**
   - Erreicht der Nutzer $\ge 100\%$, schimmert die Wasseroberfläche kurz in goldenem Glanz und ein dezentes Häkchen-Badge blendet sich ein.
