# Salus 2.0 — Barrierefreiheit & Farbfehlsichtigkeits-Engine
**Dokument:** `19-accessibility-and-colorblind-engine.md`  
**Status:** Verbindlich  
**Zweck:** Einhaltung von WCAG 2.2 AAA, Unterstützung für Protanopie, Deuteranopie und Tritanopie, `prefers-reduced-motion` und Screen-Reader-Semantik.

---

## 1. Farbfehlsichtigkeits-Paletten (OKLCH-Mapping)

Bei Rot-Grün-Schwächen (Protanopie/Deuteranopie) dürfen kritische Laborwerte oder Blutdruckwerte nicht allein durch Rot/Grün unterschieden werden:

```css
/* Modus: Deuteranopie / Protanopie aktiviert */
[data-colorblind="deuteranopia"] {
  --color-success: oklch(65% 0.18 240);   /* Blau statt Grün */
  --color-danger: oklch(75% 0.20 70);     /* Bernstein/Gelb statt Rot */
  --color-warning: oklch(70% 0.16 300);   /* Lila statt Gelb */
}

/* Modus: Tritanopie aktiviert */
[data-colorblind="tritanopia"] {
  --color-hydrate: oklch(65% 0.20 145);  /* Smaragd statt Cyan */
  --color-circadian: oklch(62% 0.22 25);  /* Karmin statt Gold */
}
```

---

## 2. Prefers-Reduced-Motion (Sensory Fallbacks)

Wenn der Nutzer Animationen im Betriebssystem deaktiviert hat:

```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* SVG-Wasserglas: Statische Füllung statt Sinuswellen */
  .wave-surface {
    display: none !important;
  }
}
```
