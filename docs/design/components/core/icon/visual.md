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
