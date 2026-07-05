## Visual Design

### Trigger
- **Avatar:** 36px (SM), `--radius-full`, `--color-slate-200` bg
- **Badge (optional):** 8px dot, top-right of avatar, `--color-error-500`

### Dropdown Panel
- **Background:** `#ffffff`, `--shadow-lg`, `--radius-lg` (12px), min-width 200px
- **Header:** Display name (`--font-body-md`, 600) + Email (`--font-caption`, `--color-slate-500`), non-interactive, padding: 12px 16px
- **Divider:** 1px `--color-slate-200`, below header
- **Items:** `--font-label-md`, padding 10px 16px, `--color-slate-700`, hover: `--color-slate-50` bg
- **Logout:** `--color-error-600` text, bold (600), separator above, last item

### States

| State | Trigger | Dropdown |
|-------|---------|----------|
| Closed | Avatar visible | Hidden |
| Open | Avatar, `--color-slate-100` bg ring (4px offset) | Visible, positioned below trigger |
| Hover (trigger) | Avatar hover: opacity 0.85 | — |

Dropdown open/close: instant (no animation). Positioned 8px below trigger, right-aligned.

### Spacing
- Trigger↔Dropdown gap: 8px
- Header padding: 12px 16px
- Item padding: 10px 16px
- Divider margin: 4px vertical

### Mobile
On `< --bp-mobile`: User menu items (Settings, Admin, Logout) move into the mobile nav drawer. Avatar becomes smaller (32px). No dropdown — items integrated in nav toggle menu.
