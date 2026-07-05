## Visual Design

### Appearance
- **Tab:** `--font-label-md`, padding 12px 16px, min-width 90px, text centered
- **Active tab:** `--color-primary` text, `2px solid --color-primary` bottom border
- **Inactive tab:** `--color-slate-600` text, transparent bottom border
- **Hover:** `--color-slate-100` bg
- **Icon (optional):** 20px, left of label, gap 8px

### Container
- Horizontal row, bottom border: `1px solid --color-slate-200` (full width)
- Active tab border overlaps container border (z-index +1)

### States

| State | Text | Bottom Border | Background |
|-------|------|--------------|------------|
| Inactive | `--color-slate-600` | transparent 2px | transparent |
| Inactive hover | `--color-slate-700` | transparent 2px | `--color-slate-100` |
| Active | `--color-primary` | `2px solid --color-primary` | transparent |
| Disabled | `--color-slate-300` | transparent 2px | transparent, opacity 0.5 |

### Variants
| Variant | Use |
|---------|-----|
| Standard | Top/bottom of content area |
| With icons | Icon + label per tab |
| Compact | Reduced padding (8px 12px), `--font-body-sm` |

### Spacing
- Tab padding: 12px 16px
- Min-width: 90px
- Icon↔Label: 8px
- Tab↔Tab: 0px (seamless)

### Mobile
Tabs overflow scroll horizontally. Fade indicators (gradient overlay) at left/right edges when content overflows.
