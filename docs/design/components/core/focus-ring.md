# Focus Ring

**Anatomy:** Visible outline around focused element indicating keyboard focus position

**Appearance:** 2px solid primary-500, 2px offset from element edge. Never use `outline: none` without a replacement.

**Default:** Browser default (dotted/dashed outline). **Override with caution.**

**Custom:** `.btn:focus-visible`: 2px primary outline, 2px offset. `.input:focus`: primary border + 2px primary-200 ring (box-shadow technique, not outline).

**Rule:** Every interactive element MUST have a visible focus indicator. Use `:focus-visible` (not `:focus`) for mouse users — they don't need focus rings, keyboard users do.

**Do:** Ensure visible focus on ALL interactive elements · Use :focus-visible · Never outline:none without replacement

**Don't:** Remove focus rings · Use :focus instead of :focus-visible · Make focus ring invisible (color matches bg)

**Token Values:**
| Token | Value |
|-------|-------|
| --focus-ring-width | 2px |
| --focus-ring-color | `{colors.primary-500}` |
| --focus-ring-offset | 2px |
| --focus-ring-style | solid |

**Related:** `skip-link.md`
