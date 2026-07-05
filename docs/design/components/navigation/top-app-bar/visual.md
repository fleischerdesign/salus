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
