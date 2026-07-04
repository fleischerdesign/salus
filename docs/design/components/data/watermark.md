# Watermark

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Semi-transparent text or pattern overlay, visible in print and on-screen

**Usage:** "CONFIDENTIAL" · "MEDICAL RECORD" · Organization logo · "DO NOT DISTRIBUTE"

**Appearance:** Rotated -45°, centered on page. Font: headline-xl, 800 weight. Color: slate-300 at 15% opacity. Print: visible at 10% opacity.

**States:** Screen (subtle, background) · Print (more visible, forced via `@media print`)

**CSS:** `position: fixed`, `pointer-events: none`, `z-index: z-debug`, `transform: rotate(-45deg)`. Only shown on medical record / doctor view pages.

**Do:** Use for sensitive documents · Keep subtle on screen · Force visible in print

**Don't:** Obscure content · Use on every page · Animate
