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
