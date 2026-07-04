# Toast / Notification

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Icon + Message + Optional action button + Close button

**Variants:** Success (tertiary) · Error (error) · Warning (warning) · Info (secondary)

**Placement:** Top-right of viewport. Stack vertically with 8px gap.

**Animation:** Slide-in from right (200ms ease-out), auto-dismiss after 5s (info/success) or persistent (error).

**States:** Entering · Visible · Dismissing (slide-out-right + fade, 200ms) · Dismissed

**Max visible:** 3 toasts at once. Older ones dismiss when new one arrives beyond limit.

**Accessibility:** `role="status"` for auto-dismiss, `role="alert"` for persistent errors. Focus should NOT move to toast.

**Do:** Use for transient feedback (save success, sync complete) · Include action for recoverable errors · Auto-dismiss non-critical toasts

**Don't:** Use for critical blocking errors (use Alert on page) · Stack more than 3 · Require user interaction for non-critical toasts
