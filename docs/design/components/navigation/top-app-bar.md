# TopAppBar

**Tokens:** `--nav-height`, `--nav-bg`, `--nav-border`, `--nav-link-font`, `--nav-link-color`, `--nav-link-hover-color`, `--nav-link-active-border`, `--nav-link-active-color`

**Anatomy:** Logo + Navigation links + Spacer + User menu

**States:** Sticky (position: sticky, top: 0, z-sticky)

**Sizes:** Height: 64px fixed. Full viewport width.

**Responsive:**
- Desktop (>1024px): Horizontal link row, dropdown menus on hover
- Tablet (601-1024px): Compact spacing, hamburger menu
- Mobile (<600px): Hamburger menu, vertical dropdown on toggle

**Active indicator:** Desktop: 2px primary border-bottom. Mobile/Tablet: 3px primary border-left + primary-50 bg.

**Dropdown behavior:** Reveal on hover with ::before bridge element (closes hover gap). Arrow icon rotates 180deg when open. Content: 8px border-radius, lg shadow.

**Do:** Use for primary navigation · Show active state for current page · Keep link labels concise

**Don't:** Nest deeper than 2 levels · Use for secondary/utility links (use User menu) · Omit mobile hamburger

**Accessibility:**
- `<nav>` element with `aria-label="Main navigation"`
- Logo: link to home with descriptive `aria-label`
- Active link: `aria-current="page"`
- Mobile hamburger: `aria-expanded="true/false"`, `aria-controls="nav-menu"`, `aria-label="Toggle navigation"`
- Dropdown triggers: `aria-expanded`, `aria-haspopup="true"`
- Keyboard: Tab through links, Enter/Space opens dropdown, Escape closes

**Composition:** Contains: Logo (Link) + Nav Links + Nav Dropdown(s) + User Menu. Fixed at top, full-width.

**Related:** `nav-dropdown.md`, `user-menu.md`, `link.md`, `drawer.md`, `breadcrumb.md`

## Visual Design

### Appearance
- **Background:** `#ffffff`
- **Border:** `1px solid --color-slate-200` (bottom)
- **Height:** 64px fixed
- **Position:** sticky, top 0
- **Z-index:** `--z-sticky` (200)
- **Shadow:** none (flat). Shadow appears only on scroll: `--shadow-sm`

### Anatomy
- Logo (left, 16px from edge) + Nav Links (flex row, center) + Spacer + User Menu (right, 16px from edge)
- Logo: `--font-headline-md` (20px, 600), `--color-primary`, text "salus"
- Nav links: `--font-label-md`, padding 12px 16px

### Link States
| State | Color | Indicator |
|-------|-------|-----------|
| Default | `--nav-link-color` (`--color-slate-600`) | none |
| Hover | `--nav-link-hover-color` (`--color-primary`) | none |
| Active (current) | `--nav-link-active-color` (`--color-primary`) | `2px solid --color-primary` bottom border |

### Desktop (> 1024px)
Horizontal nav. Dropdown menus on hover. Links: `--font-label-md`.

### Tablet (601-1024px)
Compact spacing. Nav links condensed. Hamburger menu visible.

### Mobile (< 600px)
Hamburger menu toggle (checkbox hack: `#nav-toggle` + label). Nav links hidden by default, full-width vertical dropdown on toggle open. Active indicator: `3px solid --color-primary` left border + `--color-primary-50` bg.

### Scroll Behavior
Initially transparent. On scroll > 8px: `--shadow-sm` appears. Transition: shadow 200ms ease-default.

### Spacing
- Height: 64px
- Horizontal padding: 16px sides
- Nav link padding: 12px 16px
- Link↔Link gap: 0 (flush)
