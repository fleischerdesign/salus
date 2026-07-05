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
