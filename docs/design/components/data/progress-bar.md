# Progress Bar

**Anatomy:** Track (slate-100, rounded-full, 8px height) + Fill (color varies, rounded-full, animated width)

**Color variants by context:**

| Context | Fill Color |
|---------|-----------|
| Default / Pending | `{colors.primary}` |
| Success / Fulfilled | `{colors.tertiary}` |
| Danger / Missed | `{colors.metric-heart-rate}` |

**States:** Empty (0%) · Partial · Complete (100%) · Indeterminate (animated stripe, for unknown duration)

**Animation:** Width transition 300-500ms ease-default.

**Overlay text:** Percentage centered inside fill (only when bar height ≥16px). Font: label-sm, bold, responsively colored.

**Do:** Use for quantitative progress · Animate width changes · Show percentage when bar is tall enough

**Don't:** Use for non-progress indicators · Animate too fast (>300ms) · Omit accessible label

**Accessibility:**
- `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`
- `aria-valuetext` for human-readable format (e.g., "3 of 10 steps completed")
- Indeterminate: omit `aria-valuenow` (signals unknown progress)
- Percentage text overlay: `aria-hidden="true"` (value already in aria-valuenow)

**Related:** `stat.md`, `skeleton.md`, `step-indicator.md`

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
