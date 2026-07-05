## Visual Design

### Appearance
- **Trigger:** `--font-label-sm`, `--color-slate-600`, 20px globe icon left, 4px gap, locale code right
- **Dropdown:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, min-width 160px
- **Item default:** `--font-body-sm`, padding 8px 12px, `--color-slate-700`
- **Item hover:** `--color-slate-50` bg
- **Item selected:** `--color-primary-50` bg, `--color-primary-600` text, ✓ checkmark 16px right

### States
| State | Trigger | Dropdown |
|-------|---------|----------|
| Closed | Globe icon + code | Hidden |
| Open | Globe icon + code, hover color | Visible |

### Spacing
- Trigger padding: 8px 12px
- Icon↔Code gap: 4px
- Item padding: 8px 12px
- Dropdown↔Trigger gap: 4px

### Responsive
Desktop: in top-app-bar (right, before user menu). Mobile: in settings page (list of locale options, no dropdown).
