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
