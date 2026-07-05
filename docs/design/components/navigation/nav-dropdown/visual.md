## Visual Design

### Appearance
- **Trigger:** `--font-label-md`, `--nav-link-color`, chevron icon 16px, 4px gap
- **Dropdown panel:** `#ffffff` bg, `--shadow-lg`, `--radius-md` (8px), min-width 180px
- **Items:** `--font-label-md`, padding 10px 16px, full-width, `--nav-link-color`
- **Active item:** `--color-primary` text
- **Hover item:** `--color-slate-50` bg

### States
| State | Trigger | Dropdown | Chevron |
|-------|---------|----------|---------|
| Closed | Default | Hidden | → 0° |
| Closed hover | `--nav-link-hover-color` | Hidden | → 0° |
| Open | `--nav-link-hover-color` | Visible | ↓ 180° |
| Open (hovering dropdown) | hover color | Visible | ↓ 180° |
| Active (current page) | `--nav-link-active-color` + bottom border | Hidden | → 0° |

Chevron transition: 200ms rotate ease-out.

### Hover Bridge
Invisible `::before` pseudo-element fills gap between trigger and dropdown. Prevents flicker when cursor crosses the gap. Bridge height: 4px trigger↔dropdown.

### Spacing
- Trigger padding: 12px 16px
- Trigger Chevron gap: 4px
- Dropdown↔Trigger gap: 4px
- Item padding: 10px 16px
