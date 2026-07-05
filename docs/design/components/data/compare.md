# Comparison Card

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Side-by-side or stacked comparison of two time periods. Each side: period label + value + delta

**States:** Default · Positive change (tertiary-600, ↑) · Negative change (error-600, ↓) · No change (slate-500, →) · No data ("--")

**Layout:**
- Horizontal: Left (previous) | arrow → | Right (current). Gap: 8px, arrow in center.
- Vertical: Top (current, larger) → Bottom (previous, smaller, muted).

**Period labels:** "This Week" vs "Last Week" · "July 2026" vs "July 2025" · "Today" vs "Yesterday".

**Delta:** Colored percentage/absolute change. Positive (good): tertiary-600, ↑. Negative (bad): error-600, ↓. Neutral: slate-500, →.

**Example:** Steps this week: 52,340 (↑12% vs last week). Weight today: 78.2 kg (↓1.3 kg vs last month).

**Do:** Show both periods clearly · Color-code delta direction · Use concise period labels

**Don't:** Show delta without direction · Use ambiguous period labels · Compare unrelated metrics

**Accessibility:**
- Each period value: labeled clearly (e.g., "This week: 52,340 steps")
- Delta: `aria-label` describing direction + magnitude + comparison (e.g., "Up 12% from last week")
- Arrow icon: `aria-hidden="true"`

**Related:** `card.md`, `stat.md`, `key-value.md`

## Visual Design

### Horizontal Layout
- Left (previous period): value + label, muted
- Arrow: → 18px icon, `--color-slate-400`, centered
- Right (current period): value + label + delta, prominent
- Gap: 8px between elements

### Vertical Layout
- Top (current): large value + label + delta, prominent
- Bottom (previous): smaller value + label, muted, 8px gap below top

### Colors

| Element | Color |
|---------|-------|
| Current value | `--color-on-surface` |
| Previous value | `--color-slate-500` |
| Period label | `--font-body-sm`, `--color-slate-500` |
| Positive delta | `--color-tertiary-600`, ↑ |
| Negative delta | `--color-error-600`, ↓ |
| Neutral delta | `--color-slate-500`, → |

### Delta
Arrow icon 16px + percentage/absolute value, `--font-label-sm`, 4px gap from value.

### Spacing
- Horizontal gap: 8px
- Vertical gap: 8px
- Arrow icon: 18px, centered between periods

### Responsive
`< --bp-mobile`: Horizontal → vertical layout. Arrow rotates 90° (↓) between top and bottom.

**Token Values:**
| Token | Value |
|-------|-------|
| --compare-gap | 8px |
| --compare-positive-color | `{colors.tertiary-600}` |
| --compare-negative-color | `{colors.error-600}` |
| --compare-neutral-color | `{colors.slate-500}` |
| --compare-arrow-icon-size | 18px |
| --compare-period-label-font | `var(--font-body-sm)` |

**Responsive:** Single column stack on mobile, side-by-side on desktop.
