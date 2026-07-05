# User Menu

**Tokens:** Reuses `--nav-*` tokens plus `--btn-danger-text`

**Anatomy:** Avatar trigger (36px, rounded-full) + Dropdown (user info header + action items + divider + logout)

**States:** Closed · Open (dropdown visible, lg shadow, 12px radius)

**Trigger:** Avatar with optional notification dot.

**Dropdown contents:** Display name + email (header, non-clickable), action links, hr divider, Logout (error-700, bold).

**Logout:** Explicitly styled in error color. Uses `hx-boost="false"` to force full-page navigation (clears cookies properly).

**Do:** Show user identity in trigger · Provide clear Logout · Use hx-boost=false for auth state changes

**Don't:** Place settings here (use dedicated Settings page) · Omit email for multi-account clarity

**Accessibility:**
- Trigger: Avatar with `aria-expanded="true/false"`, `aria-haspopup="true"`, `aria-label="User menu — {username}"`
- Dropdown: `role="menu"`, items: `role="menuitem"`
- Keyboard: Enter/Space opens, Arrow keys navigate, Escape closes
- Logout: distinct styling + `aria-label="Log out"` as separate from other menu items
- Header (name/email): non-interactive, for identification only

**Composition:** Trigger (Avatar + optional Badge) + Dropdown (Header text + Link list + Divider + Logout Link). Part of TopAppBar.

**Related:** `avatar.md`, `nav-dropdown.md`, `divider.md`, `badge.md`, `top-app-bar.md`

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
