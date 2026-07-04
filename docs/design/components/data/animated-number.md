# Animated Number

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Numeric display that counts up/down from previous value to new value on change

**Animation:** Ease-out, 500-800ms duration. Numbers slide-rotate vertically (like odometer) or increment linearly.

**Trigger:** Fires when new data arrives via HTMX swap. Detects value change and animates.

**Formatting:** Respects locale number formatting (commas, decimals). Integer values: no decimals during animation. Float values: fixed decimal places.

**Do:** Use for dashboard values that update · Keep animation subtle · Respect number formatting

**Don't:** Animate on page load (only on value change) · Use excessive duration · Skip animation for tiny deltas
