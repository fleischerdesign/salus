# Focus Ring

**Anatomy:** Visible outline around focused element indicating keyboard focus position

**States:** Off (no focus ring) · Keyboard Focus (`:focus-visible` — 2px solid primary-500 ring, 2px offset) · Mouse Click (`:focus` — no ring, visual change via :active state only)

**Accessibility:** Every interactive element MUST have a visible focus indicator. Use `:focus-visible` (not `:focus`) — mouse users don't need focus rings, keyboard users do. Never `outline: none` without a visible replacement. Focus order must be logical (DOM order). Custom focus rings must meet 3:1 contrast against background.

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

## Visual Design

### Appearance
- **Ring:** `2px solid --color-primary-500`, `2px` offset from element edge
- **Trigger:** `:focus-visible` only — keyboard focus, not mouse click
- **Contrast:** Minimum 3:1 against background

### Element-specific overrides
| Element | Focus Style |
|---------|------------|
| Button, Link, Tab, Checkbox | Standard ring (outline) |
| Input, Select, Textarea | Border color change + `box-shadow: 0 0 0 2px --color-primary-200` |
| Toggle, Slider | Ring on interactive element |

### Rule
Never `outline: none` without a visible replacement. Use `:focus-visible`, not `:focus`.
