## Visual Design

### Appearance
- **Background:** `--color-slate-50`
- **Border:** `1px solid --color-slate-300`
- **Radius:** `--radius-md` (8px)
- **Height:** 44px
- **Padding:** 10px 12px
- **Font:** `--font-body-md`

### Anatomy
- **Label:** above, `--font-label-md`, `--color-on-surface`, gap 4px
- **Input:** the field
- **Hint:** below, `--font-body-sm`, `--color-slate-500`, gap 4px
- **Error:** below, `--font-body-sm`, `--color-error-600`, with error icon 16px
- **Required:** asterisk `*` in `--color-error-500` after label

### States

| State | Border | Background | Other |
|-------|--------|------------|-------|
| Default | `--color-slate-300` | `--color-slate-50` | — |
| Hover | `--color-slate-400` | `--color-slate-50` | — |
| Focus | `--color-primary-500` | `#ffffff` | Ring: `0 0 0 2px --color-primary-200` |
| Error | `--color-error-400` | `--color-error-50` | Error icon right, error text below |
| Disabled | `--color-slate-200` | `--color-slate-100` | Opacity 0.5, cursor not-allowed |
| Read-only | `--color-slate-200` | `--color-slate-50` | No focus ring, cursor default |
| Filled | `--color-slate-300` | `--color-slate-50` | Clear button (×, 20px) right |

### Icon
- Left icon: 20px, `--color-slate-400`, 12px from left
- Right icon / clear: 20px, 12px from right
- With icon: padding adjusts to 38px

### Sizes & Spacing
- One size: 44px height. Textarea: min 88px
- Label↔Input: 4px. Input↔Hint/Error: 4px
- Form row gap: 16px
