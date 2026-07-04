# Viz: Number

**Anatomy:** Primary value (large, bold) + Unit (muted, smaller) + Optional delta indicator + Optional sub-label

**Sizes:**
- Small: `widget-compact-layout` — icon + value + unit side-by-side
- Medium/Large: `widget-large-layout` — value + unit stacked, sub-label below

**Delta indicator:** Positive (success, ↑) or negative (error, ↓). Shown inline next to value.

**Value formatting:** Steps: comma-separated integer. Weight: 1 decimal. Heart rate: integer + "bpm". Sleep: "Xh Ym".

**Do:** Use for single-value metrics · Show delta for trends · Keep unit compact

**Don't:** Use for multi-value comparison (use viz-bar) · Omit unit · Show delta without context

**Accessibility:**
- Value: `aria-label` with full description (e.g., "Steps today: 8,432 — up 12% from yesterday")
- Unit: included in aria-label
- Delta: aria-label describes direction + magnitude
- Fallback "--": `aria-label="No data available"`

**Related:** `stat.md`, `viz-sparkline.md`, `animated-number.md`, `key-value.md`
