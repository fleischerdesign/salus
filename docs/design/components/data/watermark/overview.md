# Watermark

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Semi-transparent text or pattern overlay, visible in print and on-screen

**Usage:** "CONFIDENTIAL" · "MEDICAL RECORD" · Organization logo · "DO NOT DISTRIBUTE"

**Appearance:** Rotated -45°, centered on page. Font: headline-xl, 800 weight. Color: slate-300 at 15% opacity. Print: visible at 10% opacity.

**States:** Screen (subtle, background) · Print (more visible, forced via `@media print`)

**CSS:** `position: fixed`, `pointer-events: none`, `z-index: z-debug`, `transform: rotate(-45deg)`. Only shown on medical record / doctor view pages.

**Do:** Use for sensitive documents · Keep subtle on screen · Force visible in print

**Don't:** Obscure content · Use on every page · Animate

**Accessibility:**
- `aria-hidden="true"` — purely decorative, no information value
- Print: forced visibility, does not interfere with content readability
- Screen readers: completely ignored

**Token Values:**
| Token | Value |
|-------|-------|
| --watermark-font | `var(--font-headline-xl)` |
| --watermark-opacity-screen | `0.15` |
| --watermark-opacity-print | `0.10` |
| --watermark-color | `{colors.slate-300}` |
| --watermark-rotation | `-45deg` |

**Related:** `print.md` (patterns/print)
