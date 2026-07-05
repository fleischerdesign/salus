# Number Stepper

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input (numeric, center-aligned) + Minus button (left) + Plus button (right)

**States:** Default · Min reached (minus disabled) · Max reached (plus disabled) · Invalid input (error border)

**Buttons:** 28px square, ghost style. Minus: `remove` icon. Plus: `add` icon. Disabled: opacity 0.5, cursor not-allowed.

**Input:** width: 56px (fits 3 digits). Text-align: center. Step: configurable (1, 0.5, 5, etc.). Min/Max: configurable.

**Keyboard:** Up/Down arrows adjust value by step size.

**Do:** Use for small numeric adjustments (reps, dosage, quantity) · Show min/max bounds · Support keyboard arrows

**Don't:** Use for large ranges (use slider) · Omit min/max enforcement · Allow non-numeric input

**Accessibility:**
- Buttons: `aria-label="Increase"` / `aria-label="Decrease"`
- Input: `type="number"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`
- Keyboard: Arrow Up/Down adjusts by step, Home/End to min/max
- Disabled buttons: `disabled` attribute at boundaries

**Token Values:**
| Token | Value |
|-------|-------|
| --stepper-btn-size | 28px |
| --stepper-input-width | 56px |
| --stepper-gap | `2px` |

**Related:** `input.md`, `slider.md`, `btn.md`

## Visual Design

### Appearance
- **Layout:** Buttons — Input — Buttons, horizontal row, gap 2px
- **Buttons:** 28×28px ghost style, 18px icon (`remove`/`add`)
- **Input:** 56px width, center-aligned text, `--font-body-md`, 44px height, `--color-slate-50` bg, `--color-slate-300` border

### States

| State | Minus Button | Input | Plus Button |
|-------|-------------|-------|------------|
| Normal range | Active (ghost, hover: slate-100) | Normal | Active (ghost, hover: slate-100) |
| At minimum | Disabled (opacity 0.5, cursor not-allowed) | Normal | Active |
| At maximum | Active | Normal | Disabled (opacity 0.5, cursor not-allowed) |
| Invalid input | Active | Error border (`--color-error-400`) | Active |

### Sizes
One size: 44px height. Input fits 3 digits (56px). Buttons: 28×28px.

### Spacing
- Button↔Input gap: 2px
- Buttons flush with input edges (no gap between button and input)
