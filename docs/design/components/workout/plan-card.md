# Plan Card

**Anatomy:** Card header (plan name + auto-regulation mode chip) + Exercise list + Actions (Start Session + Delete)

**Auto-regulation chip:** Shows mode (Disabled/Advisory/Guided). Color varies by mode.

**Exercise list:** Compact sub-rows showing: name, equipment badge, target sets×reps.

**Delete:** hx-delete with hx-swap-none + location.reload() anti-pattern. Should be replaced with targeted DOM removal.

**Do:** Show plan details at a glance · Indicate auto-regulation mode · Provide quick session start

**Don't:** Show excessive exercise detail (use session view) · Use page reload for delete
