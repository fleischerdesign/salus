# Viz: Number

**Anatomy:** Primary value (large, bold) + Unit (muted, smaller) + Optional delta indicator + Optional sub-label

**States:** Default · Positive trend (success delta) · Negative trend (error delta) · Neutral (muted delta) · No-data ("--" placeholder)

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

**Related:** `stat.md`, `viz-sparkline.md`, `anim-number.md`, `key-value.md`

## Visual Design

### Sizes

| Size | Layout | Value Font | Unit | Delta |
|------|--------|-----------|------|-------|
| Small (compact) | Icon + Value + Unit inline | `--font-headline-md` (20px, 600) | `--font-body-sm` | Right of unit |
| Medium/Large | Value + Unit stacked, sub-label below | `--font-headline-lg` (28px, 700) | `--font-body-md` | Below or right |

### Delta

| Direction | Color | Icon | Font |
|-----------|-------|------|------|
| Positive | `--color-tertiary-600` | ↑ | `--font-label-sm` |
| Negative | `--color-error-600` | ↓ | `--font-label-sm` |
| Neutral | `--color-slate-500` | → | `--font-label-sm` |

### Formatting
- Steps: `8,432` (comma-separated)
- Weight: `78.2 kg` (1 decimal)
- Heart rate: `72 bpm` (integer)
- Sleep: `7h 32m`
- No data: `"--"` em dash, `--color-slate-400`

### Spacing
- Value↔Unit: 4px
- Value↔Delta: 8px (right) or 4px (below)
- Sub-label↔Value: 4px above
