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
