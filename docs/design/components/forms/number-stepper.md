# Number Stepper

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Input (numeric, center-aligned) + Minus button (left) + Plus button (right)

**States:** Default · Min reached (minus disabled) · Max reached (plus disabled) · Invalid input (error border)

**Buttons:** 28px square, ghost style. Minus: `remove` icon. Plus: `add` icon. Disabled: opacity 0.5, cursor not-allowed.

**Input:** width: 56px (fits 3 digits). Text-align: center. Step: configurable (1, 0.5, 5, etc.). Min/Max: configurable.

**Keyboard:** Up/Down arrows adjust value by step size.

**Do:** Use for small numeric adjustments (reps, dosage, quantity) · Show min/max bounds · Support keyboard arrows

**Don't:** Use for large ranges (use slider) · Omit min/max enforcement · Allow non-numeric input
