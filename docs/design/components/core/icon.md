# Icon

**Anatomy:** Material Symbols font glyph, sized and colored consistently

**States:** Default (outlined, `currentColor`) · Filled (`fontVariationSettings: 'FILL' 1`) · Disabled (opacity 0.4)

**Accessibility:** `aria-hidden="true"` when purely decorative. `aria-label` when icon is the only interactive element content (e.g., icon-only buttons). Icon font renders as text — screen readers will read the ligature name unless explicitly hidden.

**Sizes:** Standard sizes by context:

| Context | Size |
|---------|------|
| Inline with text | 18px |
| Navigation icons | 20px |
| Button icons | 18px |
| Widget icons | 22px |
| Card header icons | 24px |
| Feature/hero icons | 40-48px |
| Empty state icons | 48px |
| Favicon-sized | 16px |

**Colors:** Default: `currentColor` (inherits parent text color). Semantically colored per context (primary, error, success).

**Variants:** Outlined (default) · Filled (`fontVariationSettings: 'FILL' 1`) — used for active/favorite states.

**Accessibility:** `aria-hidden="true"` when purely decorative. `aria-label` when icon is the only interactive element content.

**Do:** Use consistent sizing · Inherit color · Mark decorative icons as aria-hidden · Provide aria-label for icon-only buttons

**Don't:** Mix font sizes in same component · Use icon without text label in interactive elements · Skip accessibility

**Token Values:** Inherits `currentColor` from parent. Size via `font-size`. Filled variant: `fontVariationSettings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24`.

**Related:** `btn.md`, `link.md`, `avatar.md`, `status-dot.md`

## Visual Design

### Library
Material Symbols (Rounded, Google Fonts). Class: `.material-symbols-outlined`. Weight: 400. Color: `currentColor` (inherits).

### Sizes by Context

| Context | Size | Optical Size |
|---------|------|-------------|
| Inline with body text | 18px | 20px |
| Button icon | 20px (standard) / 16px (compact) | 20px |
| Navigation | 20px | 20px |
| Widget header | 22px | 24px |
| Card header | 24px | 24px |
| Empty state | 48px | 48px |
| Hero / feature | 40px | 48px |
| Favicon-sized | 16px | 20px |

### Variants
| Variant | CSS | Use |
|---------|-----|-----|
| Outlined (default) | `FILL: 0, wght: 400, GRAD: 0` | Standard |
| Filled | `FILL: 1, wght: 400, GRAD: 0` | Active, selected, favorite |

### States
| State | Visual |
|-------|--------|
| Default | Outlined, `currentColor` |
| Filled | `FILL: 1` |
| Disabled | Opacity 0.4 |

Transition outlined↔filled: instant.

### Spacing
- Icon↔Text: 4px (inline), 8px (button/header)
