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
