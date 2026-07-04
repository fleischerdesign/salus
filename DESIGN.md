---
version: "2.0"
name: Salus Health Intelligence
description: >
  A sophisticated intelligence layer for modern healthcare. Authoritative yet
  empathetic, Modern Corporate aesthetic with Minimalist lean. Targets
  clinicians, health administrators, and data analysts who require
  high-density information without cognitive fatigue.

colors:
  primary-50: "#eef2ff"
  primary-100: "#e0e7ff"
  primary-200: "#c7d2fe"
  primary-300: "#a5b4fc"
  primary-400: "#818cf8"
  primary-500: "#4f46e5"
  primary-600: "#4338ca"
  primary-700: "#3730a3"
  primary-800: "#312e81"
  primary-900: "#1e1b4b"
  primary: "#4f46e5"
  on-primary: "#ffffff"
  primary-container: "#e0e7ff"
  on-primary-container: "#1e1b4b"

  secondary-50: "#f0f9ff"
  secondary-100: "#e0f2fe"
  secondary-200: "#bae6fd"
  secondary-300: "#7dd3fc"
  secondary-400: "#38bdf8"
  secondary-500: "#0ea5e9"
  secondary-600: "#0284c7"
  secondary-700: "#0369a1"
  secondary-800: "#075985"
  secondary-900: "#0c4a6e"
  secondary: "#0ea5e9"
  on-secondary: "#ffffff"
  secondary-container: "#bae6fd"
  on-secondary-container: "#0c4a6e"

  tertiary-50: "#ecfdf5"
  tertiary-100: "#d1fae5"
  tertiary-200: "#a7f3d0"
  tertiary-300: "#6ee7b7"
  tertiary-400: "#34d399"
  tertiary-500: "#10b981"
  tertiary-600: "#059669"
  tertiary-700: "#047857"
  tertiary-800: "#065f46"
  tertiary-900: "#064e3b"
  tertiary: "#10b981"
  on-tertiary: "#ffffff"
  tertiary-container: "#d1fae5"
  on-tertiary-container: "#064e3b"

  error-50: "#fef2f2"
  error-100: "#fee2e2"
  error-200: "#fecaca"
  error-300: "#fca5a5"
  error-400: "#f87171"
  error-500: "#ef4444"
  error-600: "#dc2626"
  error-700: "#b91c1c"
  error-800: "#991b1b"
  error-900: "#7f1d1d"
  error: "#ef4444"
  on-error: "#ffffff"
  error-container: "#fee2e2"
  on-error-container: "#7f1d1d"

  warning-50: "#fffbeb"
  warning-100: "#fef3c7"
  warning-200: "#fde68a"
  warning-300: "#fcd34d"
  warning-400: "#fbbf24"
  warning-500: "#f59e0b"
  warning-600: "#d97706"
  warning-700: "#b45309"
  warning-800: "#92400e"
  warning-900: "#78350f"
  warning: "#f59e0b"

  slate-50: "#f8fafc"
  slate-100: "#f1f5f9"
  slate-200: "#e2e8f0"
  slate-300: "#cbd5e1"
  slate-400: "#94a3b8"
  slate-500: "#64748b"
  slate-600: "#475569"
  slate-700: "#334155"
  slate-800: "#1e293b"
  slate-900: "#0f172a"

  surface: "#f8f9ff"
  surface-dim: "#cbdbf5"
  surface-bright: "#f8f9ff"
  surface-container-lowest: "#ffffff"
  surface-container-low: "#eff4ff"
  surface-container: "#e5eeff"
  surface-container-high: "#dce9ff"
  surface-container-highest: "#d3e4fe"
  on-surface: "#0b1c30"
  on-surface-variant: "#464555"
  inverse-surface: "#213145"
  inverse-on-surface: "#eaf1ff"
  outline: "#777587"
  outline-variant: "#c7c4d8"
  surface-tint: "#4d44e3"
  background: "#f8f9ff"
  on-background: "#0b1c30"

  metric-heart-rate: "#f43f5e"
  metric-steps: "#f59e0b"
  metric-sleep: "#818cf8"
  metric-nutrition: "#10b981"
  metric-weight: "#6366f1"
  metric-water: "#0ea5e9"

  rank-gold: "#d4af37"
  rank-silver: "#aaa9ad"
  rank-bronze: "#b08d57"

typography:
  display:
    fontFamily: Manrope
    fontSize: 48px
    fontWeight: 800
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Manrope
    fontSize: 36px
    fontWeight: 700
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 28px
    fontWeight: 700
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: 700
    lineHeight: 32px
  headline-md:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: 600
    lineHeight: 28px
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: 400
    lineHeight: 28px
  body-md:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
  body-sm:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
  label-md:
    fontFamily: Manrope
    fontSize: 13px
    fontWeight: 600
    lineHeight: 18px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Manrope
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0.05em
  caption:
    fontFamily: Manrope
    fontSize: 11px
    fontWeight: 400
    lineHeight: 16px
  code-sm:
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', ui-monospace, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 20px
  title-sm:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: 600
    lineHeight: 20px

rounded:
  none: 0px
  xs: 2px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  2xl: 24px
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 40px
  3xl: 48px
  4xl: 64px
  unit: 4px
  container-max: 1440px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    typography: label-md
    padding: 10px 20px
  button-primary-hover:
    backgroundColor: "{colors.primary-600}"
  button-secondary:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    border: "1px solid {colors.primary}"
    rounded: "{rounded.md}"
    padding: 10px 20px
  button-secondary-hover:
    backgroundColor: "{colors.primary-50}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-ghost-hover:
    backgroundColor: "{colors.primary-50}"
  button-danger:
    backgroundColor: "{colors.error-50}"
    textColor: "{colors.error-700}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-danger-hover:
    backgroundColor: "{colors.error-100}"
  button-sm:
    backgroundColor: "{colors.slate-100}"
    textColor: "{colors.slate-700}"
    border: "1px solid {colors.slate-200}"
    rounded: "{rounded.sm}"
    padding: 6px 12px
  button-icon:
    size: 28px
    backgroundColor: transparent
    rounded: "{rounded.full}"

  card:
    backgroundColor: "#ffffff"
    border: "1px solid {colors.slate-200}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"

  input:
    backgroundColor: "{colors.slate-50}"
    border: "1px solid {colors.slate-300}"
    rounded: "{rounded.md}"
    padding: 10px 12px
    typography: body-md
  input-focus:
    border: "1px solid {colors.primary}"
    shadow: "0 0 0 2px {colors.primary-200}"

  table:
    header-bg: "{colors.slate-100}"
    header-typography: label-sm
    row-hover-bg: "{colors.slate-50}"
    border: "1px solid {colors.slate-200}"

  chip-success:
    backgroundColor: "{colors.tertiary-50}"
    textColor: "{colors.tertiary-800}"
    rounded: "{rounded.full}"
  chip-warning:
    backgroundColor: "{colors.warning-50}"
    textColor: "{colors.warning-800}"
    rounded: "{rounded.full}"
  chip-error:
    backgroundColor: "{colors.error-50}"
    textColor: "{colors.error-800}"
    rounded: "{rounded.full}"
  chip-neutral:
    backgroundColor: "{colors.slate-100}"
    textColor: "{colors.slate-600}"
    rounded: "{rounded.full}"

  modal:
    backdrop-bg: "rgba(11, 28, 48, 0.2)"
    rounded: "{rounded.xl}"
    shadow: "0 12px 24px rgba(0, 0, 0, 0.1)"
    max-width: 440px

  navigation:
    height: 64px
    bg: "#ffffff"
    border: "1px solid {colors.slate-200}"
    link-color: "{colors.slate-600}"
    link-hover-color: "{colors.primary}"
    link-active-border: "2px solid {colors.primary}"
    link-active-color: "{colors.primary}"
    link-typography: label-md

  alert-success:
    backgroundColor: "{colors.tertiary-50}"
    textColor: "{colors.tertiary-800}"
    border: "1px solid {colors.tertiary-300}"
    rounded: "{rounded.md}"
  alert-error:
    backgroundColor: "{colors.error-50}"
    textColor: "{colors.error-800}"
    border: "1px solid {colors.error-300}"
    rounded: "{rounded.md}"

  chart:
    primary: "{colors.primary-500}"
    secondary: "{colors.secondary-500}"
    benchmark: "{colors.slate-400}"
    grid: "{colors.slate-100}"
    tooltip-bg: "{colors.slate-800}"
    tooltip-text: "{colors.slate-50}"

  sleep-awake: "{colors.warning-400}"
  sleep-light: "{colors.secondary-400}"
  sleep-deep: "{colors.primary-400}"
  sleep-rem: "{colors.metric-sleep}"
---

# Salus Design System

> **Version 2.0** — `DESIGN.md` format spec (Google-compatible).
>
> This file contains the canonical machine-readable token definitions (YAML front matter above)
> plus a summary of design principles (below). Detailed documentation lives in `docs/design/`.

---

## Brand

Salus Health Intelligence is a sophisticated intelligence layer for modern healthcare.
The design style follows **Modern Corporate + Minimalism** — authoritative yet empathetic.
The palette is rooted in **Medical Indigo** (`#4f46e5`) with Sky Blue, Emerald, Red,
Amber, and Slate supporting roles. **Manrope** is the exclusive typeface.

**See:** [`docs/design/branding.md`](docs/design/branding.md)

## Architecture

Three-layer token model: **Global Tokens** (raw values) → **Semantic Tokens** (meaning)
→ **Component Tokens** (usage). Changing the primary hue requires editing one variable
(`--color-primary-500`), and all 80+ component tokens cascade automatically.

**Theming:** `:root` (light defaults) → `@media (prefers-color-scheme: dark)` (dark palette)
→ `[data-theme="dark"]` / `[data-theme="light"]` (manual override).

## Documentation Index

| Section | File |
|---------|------|
| Brand & Philosophy | [`docs/design/branding.md`](docs/design/branding.md) |
| Color Tokens | [`docs/design/tokens/colors.md`](docs/design/tokens/colors.md) |
| Typography Tokens | [`docs/design/tokens/typography.md`](docs/design/tokens/typography.md) |
| Spacing Tokens | [`docs/design/tokens/spacing.md`](docs/design/tokens/spacing.md) |
| Elevation, Radius & Z-Index | [`docs/design/tokens/elevation.md`](docs/design/tokens/elevation.md) |
| Motion & Breakpoints | [`docs/design/tokens/motion.md`](docs/design/tokens/motion.md) |
| Core Components | [`docs/design/components/core/`](docs/design/components/core/) |
| Navigation Components | [`docs/design/components/navigation/`](docs/design/components/navigation/) |
| Form Components | [`docs/design/components/forms/`](docs/design/components/forms/) |
| Data Components | [`docs/design/components/data/`](docs/design/components/data/) |
| Feedback Components | [`docs/design/components/feedback/`](docs/design/components/feedback/) |
| Dashboard Components | [`docs/design/components/dashboard/`](docs/design/components/dashboard/) |
| Sharing Components | [`docs/design/components/sharing/`](docs/design/components/sharing/) |
| Workout Components | [`docs/design/components/workout/`](docs/design/components/workout/) |
| Onboarding Components | [`docs/design/components/onboarding/`](docs/design/components/onboarding/) |
| Layout Patterns | [`docs/design/patterns/layout.md`](docs/design/patterns/layout.md) |
| Form Patterns | [`docs/design/patterns/forms.md`](docs/design/patterns/forms.md) |
| Loading Patterns | [`docs/design/patterns/loading.md`](docs/design/patterns/loading.md) |
| Full Index | [`docs/design/README.md`](docs/design/README.md) |
| Codebase Audit | [`AUDIT.md`](AUDIT.md) |

## Migration Roadmap

### Phase 1: Token Foundation (~3-4h)
Add complete 10-step color scales for all 6 families. Fix `:root` / `[data-theme="light"]`
divergence. Add `--color-warning-*` family. Define dark mode values for every token.

### Phase 2: Component Token Mapping (~2-3h)
Define all Layer 2 semantic tokens and Layer 3 component tokens. Replace 34 hardcoded hex
values in `style.css` with component token references. Consolidate shadow duplicates.

### Phase 3: Utility Class Expansion (~1-2h)
Add `.p-*`, `.text-*`, `.d-*`, `.gap-xs`, `.align-center` utilities. Remove ~60 unused CSS classes.

### Phase 4: Template Inline Style Reduction (~2-3h)
Replace ~400 inline styles with utility classes. Replace `--color-danger-*` with `--color-error-*`.

### Phase 5: Documentation (~1h)
Finalize all component spec files. Config validation tooling.

**Total: ~10-12 hours.**

## Post-Migration Metrics

| Metric | Before | After |
|--------|--------|-------|
| Undefined CSS variables | 18+ | 0 |
| Hardcoded hex colors | 34 | 0 |
| Inline styles in templates | 668 | ~150 |
| Dark-mode-broken components | 24 | 0 |
| Unused CSS classes | 60 | ~5 |

---

> **Maintenance Rule:** Any new color, spacing, or typography value introduced into
> the codebase MUST first be defined as a token in this document's YAML front matter
> before being used in CSS or templates.
