# Plan Card

**Anatomy:** Card header (plan name + auto-regulation mode chip) + Exercise list + Actions (Start Session + Delete)

**States:** Default · Hover (card shadow) · Deleting (pending confirmation) · No exercises (empty state)

**Auto-regulation chip:** Shows mode (Disabled/Advisory/Guided). Color varies by mode.

**Exercise list:** Compact sub-rows showing: name, equipment badge, target sets×reps.

**Delete:** hx-delete with hx-swap-none + location.reload() anti-pattern. Should be replaced with targeted DOM removal.

**Do:** Show plan details at a glance · Indicate auto-regulation mode · Provide quick session start

**Don't:** Show excessive exercise detail (use session view) · Use page reload for delete

**Responsive:** Full-width card on mobile. Exercise list items wrap vertically. Actions stack below card content on narrow screens.

**Accessibility:**
- Card: `role="region"` with `aria-label="Training plan: {name}"`
- Start Session: `aria-label="Start {plan name} workout"`
- Delete: `aria-label="Delete plan: {name}"`, confirmed via hx-confirm or confirmation dialog
- Auto-reg chip: `aria-label="Autoregulation mode: {mode}"`

**Composition:** Card with: Header (name + autoreg chip) + Exercise list + Start Session + Delete actions.

**Related:** `card.md`, `active-session.md`, `exercise-item.md`, `chip.md`, `btn.md`, `confirm.md`

## Visual Design

### Card
Standard card (white bg, border, radius-md), 24px padding.

### Header
- Plan name: `--font-headline-md` (20px, 600)
- Autoreg chip: right-aligned

| Mode | Chip Variant | Icon |
|------|------------|------|
| Disabled | Neutral | `block` |
| Advisory | Info (secondary) | `tips_and_updates` |
| Guided | Primary | `auto_fix_high` |

### Exercise List
- Each exercise: `--font-body-sm`, name + equipment badge (neutral chip, 14px) + "3×10 @ RPE 7" target
- Gap: 8px between exercises
- Empty state: "No exercises added" (inline, `--color-slate-400`)

### Actions
- Start Session: primary button, full-width, `play_arrow` icon 20px left
- Delete: ghost danger button, right-aligned, `delete` icon 16px

### States
| State | Card Shadow | Actions |
|-------|------------|---------|
| Default | None | Start Session visible, Delete hidden (shown on hover) |
| Hover | `--shadow-md` | Delete visible |
| Deleting | None, opacity 0.5 | Both disabled |

### Spacing
- Header↔Exercises: 16px
- Exercises↔Actions: 24px
- Exercise↔Exercise: 8px
