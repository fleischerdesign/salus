# Autoregulation Set

**Anatomy:** Set number label + Target (weight × reps @ RPE) + Actual inputs (weight, reps) + Calculated 1RM progression

**States:** Pending (shows target) · Logging (inputs visible) · Logged (dimmed, 0.75 opacity, inputs replaced with logged values)

**Target display:** Set # · Weight (bold) · "×" · Reps · "@" · RPE

**Inputs:** Two number inputs (weight, reps) side-by-side. Log button (check icon) submits. Autoreg calculated target pre-filled.

**Logged state:** Row dims to 0.75 opacity. Values shown as text. Check button becomes checkmark.

**1RM calculation:** Brzycki formula displayed below logged sets when autoreg mode active.

**Do:** Pre-fill autoreg target · Show 1RM progression · Dim completed sets

**Don't:** Allow logging without weight+reps · Omit RPE display · Show 1RM for non-autoreg plans

**Responsive:** Weight and reps inputs side-by-side on desktop, stack vertically on mobile. 1RM display collapses below inputs on narrow screens.

**Accessibility:**
- Each set: inputs with labels, `aria-label="Set {N}: weight"` / `"reps"`
- Log button: `aria-label="Log set {N}"`, `aria-busy` during submission
- Logged state: `aria-label="Set {N} logged — {weight}kg × {reps} @ RPE {rpe}"`
- 1RM calculation: `aria-label="Estimated 1RM: {value}kg"`
- Dimmed opacity: supplemented by aria-label state description

**Related:** `input.md`, `btn.md`, `stepper.md`, `stat.md`, `active-session.md`

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
