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
