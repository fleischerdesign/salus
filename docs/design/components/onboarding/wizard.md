# Wizard

**Anatomy:** Modal backdrop + Step indicator (dots) + Step content (icon + title + description + body) + Footer (Back + Next/Skip/Finish)

**States:** In-progress (step 1,2,3) · Success (completed)

**Step indicator:** 3 dots, active dot is primary-filled, inactive dots are slate-300.

**Navigation:** Back button (disabled on first step). Next button (validates form). Skip (optional, skips non-required step). Done (closes wizard).

**Body:** Step-specific content loaded via HTMX. Token generation → Entry creation → Goal creation.

**Success state:** Large success icon (48px, tertiary), congratulations message, dismiss button.

**Animation:** Step content slides in from right (250ms ease-out). Success state fades in.

**Do:** Keep steps ≤5 · Show progress indicator · Validate before advancing · Allow skip for optional steps

**Don't:** Force linear progression when optional · Omit back button · Show success before server confirms
