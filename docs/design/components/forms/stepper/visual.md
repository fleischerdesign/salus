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
