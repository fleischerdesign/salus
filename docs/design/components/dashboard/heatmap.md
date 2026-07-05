# Heatmap / Activity Calendar

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Grid of colored cells (7 columns × N rows). Each cell = one day. Color intensity shows value magnitude. Like GitHub contributions graph.

**Color scale:** 5-level sequential. Empty (slate-100, no data) → L1 (primary-50, low) → L2 → L3 → L4 (primary-700, high).

**States:** No data (empty cell, slate-100) · Data (colored cell) · Today (border: 2px primary-500) · Hover (tooltip: date + value + unit)

**Row labels:** Month names on left. Column headers: M T W T F S S (or S M T W T F S).

**Do:** Use sequential color scale · Show tooltip on hover · Highlight today · Show month labels

**Don't:** Use >5 color steps · Omit legend · Show without date context · Use diverging scale

**Accessibility:**
- Grid: `role="img"` with `aria-label` describing pattern (e.g., "Activity heatmap: highest activity on Mondays and Wednesdays")
- Individual cells: not focusable (summary in aria-label)
- Color steps: sequential palette, not diverging (red-green would fail colorblind users)
- Legend: `aria-hidden="true"` on color scale, text describes levels

**Token Values:**
| Token | Value |
|-------|-------|
| --heatmap-cell-size | 14px |
| --heatmap-cell-gap | 3px |
| --heatmap-today-border | `2px solid {colors.primary-500}` |
| --heatmap-color-steps | 5 |
| --heatmap-empty-color | `{colors.slate-100}` |

**Related:** `chart-tooltip.md`, `viz-bar.md`

## Visual Design

### Appearance
- **Grid:** 7 columns (Mon-Sun) × N rows (weeks), gap 3px
- **Cell:** 14×14px, `--radius-xs` (2px), color by value intensity
- **Month labels:** left of grid, `--font-caption` (10px), `--color-slate-500`
- **Day headers:** top of grid, `--font-caption` (10px), `--color-slate-400`, centered

### Color Scale (5 Levels)
| Level | Color | Meaning |
|-------|-------|---------|
| 0 (empty) | `--color-slate-100` | No data |
| 1 (low) | `--color-primary-100` | Lowest activity |
| 2 | `--color-primary-300` | Low-medium |
| 3 | `--color-primary-500` | Medium |
| 4 (high) | `--color-primary-700` | Highest activity |

### States
| State | Cell Border | Tooltip |
|-------|------------|---------|
| Default | none | None |
| Today | `2px solid --color-primary-500` | None |
| Hover | none | Date + value + unit (chart-tooltip) |

### Spacing
- Cell: 14×14px, gap: 3px
- Month label margin: 4px left of grid
- Day header margin: 2px above grid
