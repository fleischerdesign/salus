## Visual Design

### Appearance
- **Trigger:** matches Input: `--color-slate-50` bg, `1px --color-slate-300` border, `--radius-md`, 44px height
- **Chevron:** 20px, `--color-slate-400`, right side, 12px from right edge
- **Dropdown:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, 4px gap from trigger, max-height 280px scrollable
- **Option:** 10px 12px padding, `--font-body-md`
- **Search (optional):** text input at top of dropdown for filtering 15+ options
- **No results:** `--font-body-sm`, `--color-slate-400`, centered, padding 16px

### States

| State | Trigger Border | Chevron | Dropdown |
|-------|---------------|---------|----------|
| Default | `--color-slate-300` | 0° | hidden |
| Hover | `--color-slate-400` | 0° | hidden |
| Focus | `--color-primary-500` + ring | 0° | hidden |
| Open | `--color-primary-500` | 180° rotated | visible |
| Error | `--color-error-400` | 0° | hidden |
| Disabled | `--color-slate-200` | `--color-slate-300` | hidden, opacity 0.5 |

Chevron rotation: 150ms ease-default.

### Options

| State | Background | Text |
|-------|-----------|------|
| Default | transparent | `--color-on-surface` |
| Hover | `--color-slate-100` | `--color-on-surface` |
| Selected | `--color-primary-50` | `--color-primary-700` |
| Active (keyboard) | `--color-slate-100` | `--color-on-surface` |

### Spacing
- Label↔Select: 4px
- Trigger padding: 10px 12px
- Option padding: 10px 12px
- Dropdown↔Trigger gap: 4px

### Responsive
Full-width below `--bp-mobile`. Dropdown always matches trigger width.

### Elevation
Dropdown: Level-2 overlay. `--shadow-lg`, `--z-dropdown` (100).
