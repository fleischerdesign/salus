# Colors

> Reference: `DESIGN.md` YAML front matter (canonical values)
> Implementation: `static/style.css` `:root` / `[data-theme="dark"]` blocks

## Primary — Indigo

Purpose: Primary buttons, active navigation, key brand elements, primary chart data.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#eef2ff` | `#111827` |
| 100 | `#e0e7ff` | `#1e1b4b` |
| 200 | `#c7d2fe` | `#312e81` |
| 300 | `#a5b4fc` | `#3730a3` |
| 400 | `#818cf8` | `#4338ca` |
| 500 | `#4f46e5` | `#6366f1` |
| 600 | `#4338ca` | `#818cf8` |
| 700 | `#3730a3` | `#a5b4fc` |
| 800 | `#312e81` | `#c7d2fe` |
| 900 | `#1e1b4b` | `#e0e7ff` |

Semantic aliases: `--color-primary` → `--color-primary-500`, `--color-on-primary` → `#ffffff`, `--color-primary-container` → `--color-primary-100`

## Secondary — Sky Blue

Purpose: Informational accents, secondary visualizations, secondary buttons.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#f0f9ff` | `#082f49` |
| 100 | `#e0f2fe` | `#0c4a6e` |
| 200 | `#bae6fd` | `#075985` |
| 300 | `#7dd3fc` | `#0369a1` |
| 400 | `#38bdf8` | `#0284c7` |
| 500 | `#0ea5e9` | `#38bdf8` |
| 600 | `#0284c7` | `#7dd3fc` |
| 700 | `#0369a1` | `#bae6fd` |
| 800 | `#075985` | `#e0f2fe` |
| 900 | `#0c4a6e` | `#f0f9ff` |

## Tertiary / Success — Emerald Green

Purpose: Success states, positive health trends, system-normal indicators.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#ecfdf5` | `#022c22` |
| 100 | `#d1fae5` | `#064e3b` |
| 200 | `#a7f3d0` | `#065f46` |
| 300 | `#6ee7b7` | `#047857` |
| 400 | `#34d399` | `#059669` |
| 500 | `#10b981` | `#34d399` |
| 600 | `#059669` | `#6ee7b7` |
| 700 | `#047857` | `#a7f3d0` |
| 800 | `#065f46` | `#d1fae5` |
| 900 | `#064e3b` | `#ecfdf5` |

## Error — Red

Purpose: Errors, destructive actions, negative health indicators.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#fef2f2` | `#450a0a` |
| 100 | `#fee2e2` | `#7f1d1d` |
| 200 | `#fecaca` | `#991b1b` |
| 300 | `#fca5a5` | `#b91c1c` |
| 400 | `#f87171` | `#dc2626` |
| 500 | `#ef4444` | `#f87171` |
| 600 | `#dc2626` | `#fca5a5` |
| 700 | `#b91c1c` | `#fecaca` |
| 800 | `#991b1b` | `#fee2e2` |
| 900 | `#7f1d1d` | `#fef2f2` |

> Migration: All `--color-danger*` references must be renamed to `--color-error-*`.

## Warning — Amber

Purpose: Warning states, caution indicators, pending statuses.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#fffbeb` | `#451a03` |
| 100 | `#fef3c7` | `#78350f` |
| 200 | `#fde68a` | `#92400e` |
| 300 | `#fcd34d` | `#b45309` |
| 400 | `#fbbf24` | `#d97706` |
| 500 | `#f59e0b` | `#fbbf24` |
| 600 | `#d97706` | `#fcd34d` |
| 700 | `#b45309` | `#fde68a` |
| 800 | `#92400e` | `#fef3c7` |
| 900 | `#78350f` | `#fffbeb` |

## Neutral — Slate

Purpose: Typography, borders, subtle surfaces, scaffolding.

| Step | Light | Dark |
|------|-------|------|
| 50  | `#f8fafc` | `#0f172a` |
| 100 | `#f1f5f9` | `#1e293b` |
| 200 | `#e2e8f0` | `#334155` |
| 300 | `#cbd5e1` | `#475569` |
| 400 | `#94a3b8` | `#64748b` |
| 500 | `#64748b` | `#94a3b8` |
| 600 | `#475569` | `#cbd5e1` |
| 700 | `#334155` | `#e2e8f0` |
| 800 | `#1e293b` | `#f1f5f9` |
| 900 | `#0f172a` | `#f8fafc` |

## Surface

Material You semantic tokens for UI chrome. Exact values in `DESIGN.md` YAML front matter and `style.css` `:root` block.

## Data Visualization

| Token | Purpose | Light | Dark |
|-------|---------|-------|------|
| `metric-heart-rate` | Heart rate, protein | `#f43f5e` | `#fb7185` |
| `metric-steps` | Steps, carbs | `#f59e0b` | `#fbbf24` |
| `metric-sleep` | Sleep, deep sleep | `#818cf8` | `#a5b4fc` |
| `metric-nutrition` | Nutrition, calories | `#10b981` | `#34d399` |
| `metric-weight` | Weight, BMI | `#6366f1` | `#818cf8` |
| `metric-water` | Hydration | `#0ea5e9` | `#38bdf8` |

Sleep stages: `awake` → `warning-400`, `light` → `secondary-400`, `deep` → `primary-400`, `rem` → `metric-sleep`

## Rank Medals

| Token | Color |
|-------|-------|
| `rank-gold` | `#d4af37` |
| `rank-silver` | `#aaa9ad` |
| `rank-bronze` | `#b08d57` |
