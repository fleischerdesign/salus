# Session Timeout Warning

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Modal dialog appearing 2 minutes before session expiry. Countdown timer + "Extend Session" button + "Log Out" button

**States:** Hidden · Visible (countdown: "Session expires in 1:59") · Extended (success toast, modal closes) · Expired (redirected to login)

**Timer:** Updates every second. Last 30 seconds: numbers turn error-red, pulse animation.

**Actions:** Extend Session (renews JWT, hx-post). Log Out (redirects to /auth/logout).

**Auto-logout:** After countdown reaches 0, redirect to /auth/login with `?reason=timeout` query param.

**Do:** Warn 2 min before expiry · Show live countdown · Offer extend + logout · Auto-logout on expiry

**Don't:** Surprise user with sudden logout · Omit countdown · Block UI without escape

**Accessibility:**
- `role="dialog"` with `aria-modal="true"`, `aria-labelledby`, focus trap, Escape does nothing (must make explicit choice)
- Countdown: `aria-live="polite"` updating every second with remaining time
- Last 30s: `aria-live="assertive"` for urgency
- Buttons: "Extend Session" focused by default, "Log Out" as secondary

**Token Values:**
| Token | Value |
|-------|-------|
| --timeout-warning-duration | 120s (2 min before expiry) |
| --timeout-countdown-font | `var(--font-headline-lg)` mono |
| --timeout-urgent-color | `{colors.error-500}` |
| --timeout-urgent-threshold | 30s |

**Composition:** Modal containing: Icon (clock/warning) + Title + Countdown timer + Extend Session button + Log Out button.

**Related:** `modal.md`, `btn.md`, `icon.md`, `stat.md`
