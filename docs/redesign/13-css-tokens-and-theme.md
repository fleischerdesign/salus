# Salus 2.0 — CSS-Token-Definition & Theme-Architektur
**Dokument:** `13-css-tokens-and-theme.md`  
**Status:** Verbindlich  
**Zweck:** Vollständige Definition aller OKLCH-Farbräume, Surface-Elevationen, Typografie-Klassen, Animationen und Keyframes für `frontend/src/app.css` (Tailwind CSS v4 `@theme`).

---

## 1. Vollständiger Entwurf für `frontend/src/app.css`

```css
@import "tailwindcss";

@layer base {
  :root {
    /* ─── Farbraum: Base Surface (Light Mode) ─── */
    --color-surface-0: oklch(99% 0.002 260);      /* Reines Canvas */
    --color-surface-50: oklch(97% 0.005 260);     /* Subtile Hintergründe */
    --color-surface-100: oklch(94% 0.008 260);    /* Kachel-Hintergrund Level 1 */
    --color-surface-200: oklch(89% 0.012 260);    /* Ränder & Dividers */
    --color-surface-300: oklch(80% 0.018 260);    /* Deaktivierte Elemente */
    --color-surface-400: oklch(65% 0.025 260);    /* Muted Labels */
    --color-surface-500: oklch(48% 0.030 260);    /* Sekundärtext */
    --color-surface-600: oklch(35% 0.030 260);    /* Primär-Icon */
    --color-surface-700: oklch(25% 0.025 260);    /* Überschriften */
    --color-surface-800: oklch(18% 0.020 260);    /* Tiefer Text */
    --color-surface-900: oklch(12% 0.015 260);    /* Fast Schwarz */

    /* ─── Semantische Marken- & Domänen-Farben ─── */
    --color-primary-50: oklch(96% 0.04 250);
    --color-primary-500: oklch(58% 0.22 255);    /* Salus Electric Iris */
    --color-primary-600: oklch(50% 0.22 255);

    --color-vital: oklch(62% 0.22 25);           /* Kardiologie & Blutdruck (Karmin) */
    --color-vital-bg: oklch(96% 0.04 25);

    --color-activity: oklch(65% 0.20 45);        /* Workouts & Bewegung (Koralle/Amber) */
    --color-activity-bg: oklch(96% 0.04 45);

    --color-hydrate: oklch(68% 0.16 230);        /* Wasser & Hydration (Cyan/Ozean) */
    --color-hydrate-bg: oklch(96% 0.04 230);

    --color-fasting: oklch(66% 0.18 310);        /* Fasten & Autophagie (Amethyst) */
    --color-fasting-bg: oklch(96% 0.04 310);

    --color-circadian: oklch(78% 0.16 85);       /* Sonnen- & Zirkadian-Rhythmus (Gold) */
    --color-circadian-bg: oklch(97% 0.04 85);

    --color-success: oklch(66% 0.19 145);        /* Optimale Laborwerte & Habits (Smaragd) */
    --color-warning: oklch(75% 0.17 75);         /* Grenzwertige Laborwerte (Bernstein) */
    --color-danger: oklch(58% 0.22 28);          /* Kritische Werte & Löschen (Rubin) */

    /* ─── Radien ─── */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 18px;
    --radius-xl: 26px;
    --radius-full: 9999px;

    /* ─── Elevationen & Schatten ─── */
    --shadow-subtle: 0 1px 3px oklch(0% 0 0 / 0.04), 0 1px 2px oklch(0% 0 0 / 0.02);
    --shadow-card: 0 4px 16px -2px oklch(0% 0 0 / 0.06), 0 2px 6px -1px oklch(0% 0 0 / 0.03);
    --shadow-lift: 0 12px 32px -4px oklch(0% 0 0 / 0.10), 0 4px 12px -2px oklch(0% 0 0 / 0.05);
    --shadow-glow-primary: 0 0 24px -4px oklch(58% 0.22 255 / 0.35);
  }

  .dark {
    /* ─── Farbraum: Base Surface (Dark Mode / OLED Optimized) ─── */
    --color-surface-0: oklch(10% 0.012 260);      /* Canvas Tiefschwarz */
    --color-surface-50: oklch(14% 0.015 260);     /* Kacheln Level 0 */
    --color-surface-100: oklch(18% 0.018 260);    /* Kacheln Level 1 */
    --color-surface-200: oklch(24% 0.020 260);    /* Ränder & Dividers */
    --color-surface-300: oklch(32% 0.022 260);    /* Deaktivierte Elemente */
    --color-surface-400: oklch(50% 0.025 260);    /* Muted Labels */
    --color-surface-500: oklch(65% 0.025 260);    /* Sekundärtext */
    --color-surface-600: oklch(80% 0.020 260);    /* Primär-Icon */
    --color-surface-700: oklch(90% 0.012 260);    /* Text Hell */
    --color-surface-800: oklch(95% 0.008 260);    /* Überschriften */
    --color-surface-900: oklch(99% 0.002 260);    /* Reines Weiß */

    --shadow-subtle: 0 1px 3px oklch(0% 0 0 / 0.25);
    --shadow-card: 0 4px 16px -2px oklch(0% 0 0 / 0.40);
    --shadow-lift: 0 12px 32px -4px oklch(0% 0 0 / 0.60);
    --shadow-glow-primary: 0 0 28px -2px oklch(58% 0.22 255 / 0.45);
  }
}

/* ─── Typografische Optimierungen ─── */
body {
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  background-color: var(--color-surface-0);
  color: var(--color-surface-800);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.tabular-nums {
  font-variant-numeric: tabular-nums;
}

/* ─── Keyframe Animationen (Visual Delight Engine) ─── */
@keyframes waveMotion {
  0% { transform: translateX(0) translateZ(0) scaleY(1); }
  50% { transform: translateX(-25%) translateZ(0) scaleY(1.08); }
  100% { transform: translateX(-50%) translateZ(0) scaleY(1); }
}

.animate-wave {
  animation: waveMotion 6s cubic-bezier(0.36, 0, 0.66, -0.56) infinite;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}

.animate-shimmer {
  animation: shimmer 1.6s infinite;
}

@keyframes pulseGlow {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.04); }
}

.animate-pulse-glow {
  animation: pulseGlow 3s ease-in-out infinite;
}
```
