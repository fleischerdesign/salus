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

## Visual Design

### Appearance
- Modal (see `modal.md`): Backdrop + Content panel, max-width 400px
- Icon: clock/warning 48px, `--color-warning-500`, centered
- Title: `--font-headline-md`, centered, "Session Expiring"
- Timer: `--font-headline-lg` (28px, 700), monospace (`--font-family-mono`), centered, `--color-on-surface`

### States

| State | Timer Color | Animation | Actions |
|-------|-----------|-----------|---------|
| Visible (120-31s) | `--color-on-surface` | None | Extend + Log Out |
| Urgent (30-0s) | `--color-error-500` | Pulse opacity 1→0.6→1, 1s infinite | Extend + Log Out |
| Extended | — | Toast "Session extended" (success variant) | — |
| Expired | — | Redirect to /auth/login?reason=timeout | — |

### Anatomy
- Icon (48px, centered) → Title → Countdown timer (monospace digits MM:SS) → Description ("Your session will expire due to inactivity") → Buttons (row, gap 8px)

### Buttons
- Extend Session: Primary button, `hx-post` to refresh JWT
- Log Out: Ghost/Secondary button, redirects to /auth/logout

### Spacing
- Icon↔Title: 16px
- Title↔Timer: 8px
- Timer↔Description: 8px
- Description↔Buttons: 24px
- Button↔Button: 8px

### Focus & Behavior
- Escape: ignored (must make explicit choice)
- Default focus: "Extend Session" button
- Timer updates every second via JS (`Date.now()` until expiry)
- Last 30 seconds: `aria-live="assertive"` for urgency
