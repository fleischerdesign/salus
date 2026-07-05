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
