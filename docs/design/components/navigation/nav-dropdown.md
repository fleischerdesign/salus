# Nav Dropdown

**Tokens:** `--nav-dropdown-bg`, `--nav-dropdown-border`, `--nav-dropdown-shadow`, `--nav-dropdown-radius`

**Anatomy:** Trigger link (label-md, with arrow icon) + Dropdown panel

**States:** Closed · Open (on hover, lg shadow, 8px radius, arrow rotates 180deg)

**Contents:** Link list (label-md, full-width, hover: slate-50 bg). Active link: primary text.

**Interaction:** CSS :hover reveal with ::before bridge element (prevents hover-gap flicker). Sub-second delay on mouseleave.

**Do:** Use for grouped navigation · Keep dropdown width auto-fit · Limit to 2 levels

**Don't:** Nest dropdowns deeper than 2 levels · Omit hover bridge · Make items too long (>25 chars)

**Accessibility:**
- Trigger: `aria-expanded="true/false"`, `aria-haspopup="true"`
- Dropdown: `role="menu"`, items: `role="menuitem"`
- Keyboard: Enter/Space opens, Arrow keys navigate items, Escape closes, Tab moves to next trigger
- Mouse: `:hover` opens, mouseleave closes with 200ms delay
- Active item: `aria-current="page"` if on current page

**Composition:** Trigger (Link + Arrow icon) + Dropdown panel (list of Links). Part of TopAppBar.

**Related:** `top-app-bar.md`, `user-menu.md`, `link.md`, `context-menu.md`

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
