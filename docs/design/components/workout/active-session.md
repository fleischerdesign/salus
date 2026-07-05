# Active Session

**Anatomy:** Recovery score badge + Exercise list (with target sets/reps/RPE) + Body notes textarea + Complete Session button

**States:** Active · Completing · Completed (redirect)

**Exercise rows:** Name + Target (sets×reps @ RPE) + Logged sets sub-list + Log Set button

**Logged set:** Weight input + Reps input + RPE display + Check button. Logged sets dim to 0.75 opacity.

**Autoregulation indicator:** Show "Autoregulated" chip when plan has autoreg mode enabled. Show calculated 1RM progression.

**Complete Session:** POST form with notes textarea. Full-page redirect on success.

**Do:** Show real-time autoreg calculated targets · Disable log button when set count exceeds target · Show progress toward target sets

**Don't:** Allow logging without weight/reps · Omit warmup indicator · Forget rest timer between sets

**Responsive:** Single column on mobile — exercises and sets stack vertically. Inputs inline on desktop, full-width on mobile.

**Accessibility:**
- Each set row: distinct inputs with labels, `aria-label` describes set number
- Log button: `aria-label="Log set {N}"`, `aria-busy` during submission
- Logged state: `aria-label="Set {N} logged — {weight}kg × {reps} @ RPE {rpe}"`
- Recovery score: `aria-label` describing readiness
- Autoreg indicator: `aria-label="Autoregulated — {mode}"`

**Composition:** Header (plan name + autoreg chip) + Exercise list + Body notes + Complete button. Each exercise: name + targets + set rows with log.

**Related:** `plan-card.md`, `autoregulation-set.md`, `btn.md`, `input.md`, `chip.md`, `stat.md`

## Visual Design

### Header
- Plan name: `--font-headline-md` (20px, 600)
- Autoreg chip: neutral chip showing mode (Disabled/Advisory/Guided)
- Recovery score: badge with `--font-headline-md` number + colored chip (normal/warning/error)
- Gap: 8px between elements

### Exercise Row
- Name: `--font-body-md` (16px, 600)
- Target: `--font-body-sm`, `--color-slate-500` (e.g., "3×10 @ RPE 7")
- Logged sets: count chip, `--font-label-sm` (e.g., "2/3 sets")
- Log button: ghost sm, `add` icon 18px, right-aligned

### Logged Set Row
- Dimmed: opacity 0.75, logged values as text
- Weight: `--font-body-md` bold + "kg"
- Reps: `--font-body-sm`, `--color-slate-500`
- RPE: `--font-label-sm`, `--color-slate-500`

### Complete Button
Primary, full-width, margin-top 24px.

### Spacing
- Exercise↔Exercise: 24px gap
- Set↔Set: 8px gap
