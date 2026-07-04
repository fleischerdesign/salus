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

**Accessibility:**
- `role="status"` (auto-dismiss) or `role="alert"` (persistent). Use `aria-live="polite"` for info/success, `aria-live="assertive"` for errors.
- Focus does NOT move to toast
- Dismiss button: `aria-label="Dismiss notification"`
- Multiple toasts: each in its own live region for independent announcements

**Token Values:**
| Token | Value |
|-------|-------|
| --toast-max-width | 360px |
| --toast-shadow | `var(--shadow-lg)` |
| --toast-radius | `var(--radius-md)` |
| --toast-gap | `8px` |
| --toast-duration | 5s (auto-dismiss) |
| --toast-animation-in | slide-in-right 200ms ease-out |
| --toast-animation-out | slide-out-right 200ms ease-in |
| --toast-z-index | `var(--z-tooltip)` |
| --toast-max-visible | 3 |

**Composition:** Icon + Message + optional Action button + Close button. Positioned top-right viewport corner.

**Responsive:** Full-width on mobile with slight horizontal margin.

**Related:** `alert.md`, `btn.md`, `icon.md`
