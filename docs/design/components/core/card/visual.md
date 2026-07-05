## Visual Design

### Appearance
- **Background:** `#ffffff`
- **Border:** `1px solid --color-slate-200`
- **Shadow (default):** none (flat)
- **Shadow (hover):** `--shadow-md` (0 4px 12px rgba(0,0,0,0.05))
- **Radius:** `--radius-md` (8px)

### Variants
| Variant | Background | Border | Shadow |
|---------|-----------|--------|--------|
| Default | `#ffffff` | `1px --color-slate-200` | none → hover: `--shadow-md` |
| Elevated | `#ffffff` | `1px --color-slate-200` | `--shadow-sm` by default |
| Outlined | `#ffffff` | `1px --color-slate-200` | none |
| Flat | `--color-slate-50` | none | none |

### Anatomy
- Header (optional): Icon (24px) + Title (`--font-headline-md`) + Action button (right-aligned)
- Body: freeform content
- Footer (optional): action buttons, right-aligned, gap 8px

### Sizes & Spacing
| Property | Value |
|----------|-------|
| Padding | 24px (`--space-lg`) |
| Header↔Body gap | 16px (`--space-md`) |
| Body↔Footer gap | 16px |
| Card↔Card gap | 16px |

### States
| State | Visual | Duration |
|-------|--------|----------|
| Default | White bg, border, no shadow | — |
| Hover | `--shadow-md` appears | 150ms ease-default |
| Clickable card | Cursor pointer, full card interactive | — |

### Responsive
- `< --bp-mobile`: Full-width, padding 16px
- `> --bp-mobile`: Grid layout, padding 24px
