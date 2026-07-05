# Badge (Notification Count)

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Small circle/dot with numeric count, absolutely positioned on the corner of a parent element (avatar, icon, nav link)

**States:** Hidden (count is 0) · Visible (count > 0) · Overflow ("99+" when count > 99)

**Sizes:** Small dot (8px, count not shown — presence only) · Standard (18px, 1-2 digit count)

**Appearance:** Error-500 background, on-error text, label-sm font (10px). Rounded-full. No padding (centered text).

**Position:** Top-right corner of parent, -4px offset (overlaps parent edge). Parent must have `position: relative`.

**Animation:** Scale-in on appear (150ms ease-out). No animation on count change (jarring when numbers rapidly change).

**Do:** Use for notification counts, unread indicators · Show "99+" for overflow · Absolute position on parent

**Don't:** Use as a status indicator (use Chip) · Animate count changes · Show for zero count · Use without parent position:relative

**Accessibility:**
- `aria-label="{count} unread notifications"` or similar descriptive text
- Number: visually shown, also in aria-label for screen readers
- Parent element: `aria-describedby` referencing badge if badge conveys status
- Dot variant (no count): `aria-label="Unread"` or "Active"

**Token Values:**
| Token | Value |
|-------|-------|
| --badge-bg | `{colors.error-500}` |
| --badge-text | `{colors.on-error}` |
| --badge-dot-size | 8px |
| --badge-standard-size | 18px |
| --badge-font | `10px / 700 var(--font-family-primary)` |
| --badge-overflow-threshold | 99 |
| --badge-overflow-text | "99+" |

**Related:** `chip.md`, `status-dot.md`, `avatar.md`

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
