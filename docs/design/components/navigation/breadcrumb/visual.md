## Visual Design

### Appearance
- **Layout:** Horizontal row, `--font-body-sm` (14px), gap 8px between segments
- **Link default:** `--color-slate-500`, no underline
- **Link hover:** `--color-primary`, no underline
- **Current (last):** `--color-slate-900`, bold (600), not clickable
- **Separator:** `/` character, `--color-slate-400`, 8px gap both sides
- **Container:** `<nav>` below top-app-bar, 16px vertical padding

### States

| Segment | Color | Weight | Clickable |
|---------|-------|--------|-----------|
| Link (default) | `--color-slate-500` | 400 | Yes |
| Link (hover) | `--color-primary` | 400 | Yes |
| Current | `--color-slate-900` | 600 | No |
| Current (hover) | No change | 600 | No |

### Mobile Collapse
On `< --bp-mobile`: show only last 1-2 segments. Earlier segments collapsed to "..." dropdown trigger. Dropdown: ghost button, 24×24px, `more_horiz` icon. Click shows full breadcrumb in dropdown (same style as nav-dropdown).

### Spacing
- Segment gap: 8px (4px each side of separator)
- Separator: 4px each side
- Container padding: 16px top/bottom
