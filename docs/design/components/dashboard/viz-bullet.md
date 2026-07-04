# Bullet Chart

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Horizontal bar showing: Qualitative ranges (colored background bands) + Performance measure (dark bar) + Comparative measure (vertical tick mark)

**Structure:**
1. Background bands: sequential shades (e.g., slate-100, slate-200, slate-300) — "poor", "satisfactory", "good" ranges
2. Performance bar: primary-600, shorter than bands. Shows actual value.
3. Target marker: vertical line/tick at target value. Black or primary-900.

**Example:** Weight loss: bands = poor (0-2kg), satisfactory (2-5kg), good (5-10kg). Bar = actual (7kg). Tick = goal (8kg).

**Do:** Use for goal-vs-actual with qualitative context · Keep 3-5 bands · Show target clearly

**Don't:** Use for simple progress (use progress-bar) · Omit qualitative bands · Confuse with stacked bar

**Accessibility:**
- Bar: `role="img"` with `aria-label` describing actual vs target within qualitative context (e.g., "Weight loss: 7kg actual, 8kg target — in 'good' range")
- Bands: qualitative ranges learned from aria-label, not individually interactive

**Token Values:**
| Token | Value |
|-------|-------|
| --bullet-bar-height | 24px |
| --bullet-band-poor | `{colors.slate-100}` |
| --bullet-band-satisfactory | `{colors.slate-200}` |
| --bullet-band-good | `{colors.slate-300}` |
| --bullet-performance-color | `{colors.primary-600}` |
| --bullet-target-color | `{colors.slate-900}` |
| --bullet-target-width | 2px |

**Related:** `progress-bar.md`, `viz-bar.md`, `comparison-card.md`
