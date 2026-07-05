## Visual Design

### Appearance
- **Border:** `1px solid --color-slate-200` (between rows and columns)
- **Header:** `--color-slate-100` bg, `--font-label-sm` (12px, 500), `--color-slate-700`, uppercase, padding 10px 16px
- **Row:** `#ffffff` bg (default), `--font-body-sm` (14px), padding 12px 16px, height 48px
- **Hover:** `--color-slate-50` bg on entire row

### States
| State | Row Background | Border |
|-------|---------------|--------|
| Default | `#ffffff` | `--color-slate-200` |
| Hover | `--color-slate-50` | `--color-slate-200` |
| Selected/Active | `--color-primary-50` | `--color-slate-200` |
| Empty | Empty state component in colspan cell | — |

### Compact Variant
- Row height: 36px, padding: 8px 12px
- Font: `--font-body-sm` (14px). Header: `--font-label-sm` (12px)

### Cell Content
Allowed: Link, Button, Chip, Badge, Icon, KeyValue, `--font-body-sm` text.
Actions: right-aligned, 4px gap between action buttons.

### Spacing
- Cell padding: 12px 16px (standard), 8px 12px (compact)
- Row height: 48px (standard), 36px (compact)

### Responsive
Full-width with horizontal scroll on mobile. Sticky first column optional. Min column width: 100px.
