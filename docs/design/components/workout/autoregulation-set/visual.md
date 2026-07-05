## Visual Design

### Set Row Layout
- Set number: `--font-label-sm` (12px, 600), `--color-slate-500`, left, 24px width
- Target: `--font-body-md`, bold (e.g., "80kg × 8 @ RPE 7")
- Inputs: 2 steppers (weight, reps), side-by-side, gap 8px. Width: 72px each
- Log button: 28×28px ghost, `check` icon 18px, states: default/hover/logged

### States

| State | Target | Inputs | Button | Row Opacity |
|-------|--------|--------|--------|------------|
| Pending | Visible | Visible, pre-filled | Default (ghost) | 1.0 |
| Logging | Visible | Active | Active | 1.0 |
| Logged | Hidden | Replaced with logged values | ✓ checkmark icon | 0.75 |
| Disabled (max sets) | Visible | Disabled | Disabled | 0.5 |

### 1RM Display
`--font-label-sm`, `--color-slate-500`. Below logged sets, formula: "Est. 1RM: 95kg". Only shown when autoreg mode is active.

### Spacing
- Set# column: 24px
- Input gap: 8px
- Input↔Log button: 8px
- Set↔Set gap: 4px
