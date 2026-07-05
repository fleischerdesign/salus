# Step Indicator

**Anatomy:** Row of dots or numbered circles showing progress through a sequence

**States:** Pending (slate-300, unfilled) · Active (primary-500, filled) · Completed (success/tertiary, checkmark or filled) · Error (error-500, alert icon)

**Variants:**
- Dots (onboarding wizard, 2-5 steps): 8px circles, active dot is primary-filled
- Numbers (multi-page form, 3-10 steps): 24px circles with step number, active has primary bg + white text
- Labels (detailed workflow): circle + step title below

**Spacing:** 8px gap between dots. 16px between numbered steps.

**Accessibility:** Use `<ol>` with `<li>` elements. `aria-current="step"` on active step. Progressive disclosure — show step title for screen readers.

**Do:** Show progress visually · Use semantic element (ol) · Distinguish active clearly

**Don't:** Use for <2 or >10 steps · Omit screen reader context · Skip error state

**Token Values:**
| Token | Value |
|-------|-------|
| --step-dot-size | 8px |
| --step-number-size | 24px |
| --step-pending-color | `{colors.slate-300}` |
| --step-active-color | `{colors.primary-500}` |
| --step-completed-color | `{colors.tertiary-500}` |
| --step-error-color | `{colors.error-500}` |

**Responsive:** Spacing reduces on mobile (8px→6px gap). Vertical labels may stack below dots.

**Related:** `wizard.md`, `progress-bar.md`

## Visual Design

### Variants

| Variant | Step Shape | Size | Content | Max Steps |
|---------|-----------|------|---------|-----------|
| Dots | Circle | 8px | None | 2-5 |
| Numbers | Circle with number | 24px | White number, `--font-label-sm` (10px, 700) | 3-10 |
| Labels | Circle + text below | 24px circle + `--font-body-sm` label | Step title below | 3-6 |

### Colors

| State | Dot/Number Fill | Number Color | Connector Line | Icon |
|-------|----------------|-------------|----------------|------|
| Pending | `--color-slate-300` | `--color-slate-500` | `--color-slate-200` | — |
| Active | `--color-primary-500` | `#ffffff` | In progress (left: primary, right: slate-200) | — |
| Completed | `--color-tertiary-500` | `#ffffff` | `--color-tertiary-200` | white ✓ 12px |
| Error | `--color-error-500` | `#ffffff` | `--color-error-200` | white ! 12px |

### Connector Line
2px height, between dot and next dot. Color per state above. Gap: 0px between dot and connector.

### Spacing
- Dot variant: 8px gap between dots
- Number variant: 16px gap between steps
- Label variant: 24px gap between steps

### Responsive
`< --bp-mobile`: Gap reduces (8→6px for dots, 16→12px for numbers). Labels stack below circles.
