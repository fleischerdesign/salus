# Animated Number

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Numeric display that counts up/down from previous value to new value on change

**States:** Static (showing current value) · Animating-up (counting up, 500-800ms) · Animating-down (counting down) · No-data ("--")

**Animation:** Ease-out, 500-800ms duration. Numbers slide-rotate vertically (like odometer) or increment linearly.

**Trigger:** Fires when new data arrives via HTMX swap. Detects value change and animates.

**Formatting:** Respects locale number formatting (commas, decimals). Integer values: no decimals during animation. Float values: fixed decimal places.

**Do:** Use for dashboard values that update · Keep animation subtle · Respect number formatting

**Don't:** Animate on page load (only on value change) · Use excessive duration · Skip animation for tiny deltas

**Accessibility:**
- `aria-live="polite"` announces the new value after animation completes
- `aria-label` with final value + unit (screen readers don't need to "watch" the animation)
- Respects `prefers-reduced-motion`: skip animation, show final value immediately

**Token Values:**
| Token | Value |
|-------|-------|
| --anim-number-duration | 800ms |
| --anim-number-easing | `var(--ease-out)` |
| --anim-number-min-delta | 1 (skip animation for smaller changes) |

**Related:** `stat.md`, `spinner.md`

## Visual Design

### Appearance
- **Font:** inherits from parent stat component (`--font-headline-lg` or `--font-headline-md`)
- **Color:** `--color-on-surface`
- **Formatting:** locale-aware (commas, decimals). Integer: no decimals during animation

### Animation
- **Type:** Linear count-up/down from old value to new value
- **Duration:** 800ms ease-out (configurable per context)
- **Minimum delta:** 1 (skip animation for smaller changes)
- **Trigger:** HTMX swap detection — only animate on value change, not on initial load

### States
| State | Visual |
|-------|--------|
| Static | Current value displayed |
| Animating up | Numbers counting up, final digit settles last |
| Animating down | Numbers counting down |
| No data | "--" em dash, `--color-slate-400` |

### Respects `prefers-reduced-motion`
Skip animation entirely, show final value immediately.
