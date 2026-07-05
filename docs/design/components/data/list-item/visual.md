## Visual Design

### Appearance
- **Container:** vertical list, no border-top, 1px `--color-slate-200` border-bottom per item
- **Padding:** 12px 16px (standard), 8px 12px (compact)
- **Icon (optional):** 20px, left, `--color-slate-400`, gap 12px to content
- **Primary text:** `--font-body-md`, `--color-on-surface`
- **Secondary text:** `--font-body-sm`, `--color-slate-500`, below primary, 2px gap
- **Action (optional):** icon button (28×28px ghost), right-aligned

### Variants

| Variant | Padding | Font |
|---------|---------|------|
| Standard | 12px 16px | `--font-body-md` |
| Compact | 8px 12px | `--font-body-sm` |
| With actions | 12px 16px + right actions | `--font-body-md` |
| With metadata | 12px 16px + secondary line | `--font-body-md` + `--font-body-sm` |

### States

| State | Background |
|-------|-----------|
| Default | `#ffffff` |
| Hover | `--color-slate-50` |
| Active/Selected | `--color-primary-50` |
| Disabled | opacity 0.5, cursor not-allowed |

### Spacing
- Icon↔Content: 12px
- Primary↔Secondary text: 2px
- Action↔Content: 16px
- Item↔Item: 0px (border-bottom separates)
