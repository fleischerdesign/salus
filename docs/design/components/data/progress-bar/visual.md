## Visual Design

### Appearance
- **Track:** `--color-slate-100` bg, `--radius-full`, 8px height (standard), full width
- **Fill:** `--radius-full`, animated width transition
- **Overlay text:** `--font-label-sm` (12px, 700), centered in fill. Hidden when bar < 16px tall.

### Color Variants

| Context | Fill Color | Stripes |
|---------|-----------|---------|
| Default / Pending | `--color-primary` | No |
| Success / Complete | `--color-tertiary` | No |
| Warning / Partial | `--color-warning` | No |
| Danger / Missed | `--color-error` | No |
| Indeterminate | `--color-primary` | Animated diagonal stripes |

### Sizes
| Size | Height | Text Visible |
|------|--------|-------------|
| Standard | 8px | No |
| Large | 16px | Yes (inside) |
| Thin | 4px | No |

### States
| State | Fill Width | Animation |
|-------|-----------|-----------|
| Empty (0%) | 0% | — |
| Partial (1-99%) | percentage% | Width 500ms ease-default |
| Complete (100%) | 100% | Width 500ms ease-default |
| Indeterminate | ~30% stripe slides | Stripes: 1.5s linear infinite |

### Spacing
- Margin: 8px above/below when in card or section
- Label (if present): above bar, `--font-label-sm`, `--color-slate-600`, 4px gap
