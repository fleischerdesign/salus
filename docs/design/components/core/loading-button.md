# Loading Button

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Spinner (centered, replaces label) within button body.

**States:** Default · Loading (disabled, spinner visible, label hidden but preserves width) · Success (check icon, 2s display, returns to default) · Error (alert icon, reverts after 2s)

**Spinner:** 16px, border-based CSS animation, primary color. Centered within button.

**Implementation:** Button width preserved during loading (text visibility: hidden, not display: none) to prevent layout shift. `aria-busy="true"` while loading, `aria-live="polite"` for status changes.

**Do:** Preserve button width during loading · Show success briefly after completion · Disable during loading

**Don't:** Shrink button when spinner appears · Leave button in loading state indefinitely · Forget error feedback
