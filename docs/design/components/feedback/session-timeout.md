# Session Timeout Warning

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Modal dialog appearing 2 minutes before session expiry. Countdown timer + "Extend Session" button + "Log Out" button

**States:** Hidden · Visible (countdown: "Session expires in 1:59") · Extended (success toast, modal closes) · Expired (redirected to login)

**Timer:** Updates every second. Last 30 seconds: numbers turn error-red, pulse animation.

**Actions:** Extend Session (renews JWT, hx-post). Log Out (redirects to /auth/logout).

**Auto-logout:** After countdown reaches 0, redirect to /auth/login with `?reason=timeout` query param.

**Do:** Warn 2 min before expiry · Show live countdown · Offer extend + logout · Auto-logout on expiry

**Don't:** Surprise user with sudden logout · Omit countdown · Block UI without escape
