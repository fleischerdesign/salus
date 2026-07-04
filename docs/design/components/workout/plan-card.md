# Plan Card

**Anatomy:** Card header (plan name + auto-regulation mode chip) + Exercise list + Actions (Start Session + Delete)

**Auto-regulation chip:** Shows mode (Disabled/Advisory/Guided). Color varies by mode.

**Exercise list:** Compact sub-rows showing: name, equipment badge, target sets×reps.

**Delete:** hx-delete with hx-swap-none + location.reload() anti-pattern. Should be replaced with targeted DOM removal.

**Do:** Show plan details at a glance · Indicate auto-regulation mode · Provide quick session start

**Don't:** Show excessive exercise detail (use session view) · Use page reload for delete

**Accessibility:**
- Card: `role="region"` with `aria-label="Training plan: {name}"`
- Start Session: `aria-label="Start {plan name} workout"`
- Delete: `aria-label="Delete plan: {name}"`, confirmed via hx-confirm or confirmation dialog
- Auto-reg chip: `aria-label="Autoregulation mode: {mode}"`

**Composition:** Card with: Header (name + autoreg chip) + Exercise list + Start Session + Delete actions.

**Related:** `card.md`, `active-session.md`, `exercise-item.md`, `chip.md`, `button.md`, `confirmation-dialog.md`
