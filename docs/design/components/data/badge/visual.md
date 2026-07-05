## Visual Design

### Appearance
- **Standard:** 18px circle, `--color-error-500` bg, `--color-on-error` text
- **Dot:** 8px circle, `--color-error-500` bg, no text
- **Font:** 10px, 700 weight, `--font-family-primary`, centered
- **Radius:** `--radius-full`
- **Position:** Top-right of parent, -4px offset. Parent needs `position: relative`

### States
| State | Condition | Visual |
|-------|-----------|--------|
| Hidden | Count = 0 | `display: none` |
| Visible | Count 1–99 | Number displayed, scale-in 150ms ease-out |
| Overflow | Count > 99 | "99+" displayed |

### Animation
- Appear: scale 0→1 (150ms ease-out)
- Count change: instant (no animation)
- Exit: scale 1→0 (150ms ease-in)

### Sizes
| Size | Diameter | Font | Shows |
|------|----------|------|-------|
| Dot | 8px | — | Presence only |
| Standard | 18px | 10px/700 | 1–2 digit count |

### Color Variants
- Default: `--color-error-500` (notifications, unread)
- Neutral: `--color-slate-500` (non-urgent counts)
- Success: `--color-tertiary-500` (positive confirmations, rare)
