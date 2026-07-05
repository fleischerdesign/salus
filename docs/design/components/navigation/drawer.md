# Drawer

> **Status: Design spec only — not yet implemented.**

**Anatomy:** Slide-out panel (left, 280px) + Backdrop overlay + Close button + Header + Navigation links + Footer

**States:** Closed · Opening (slide-in from left, 200ms ease-out) · Open · Closing

**Contents:** Same as mobile nav but with dedicated close affordance. Can include nested sections with collapsible headers.

**Backdrop:** Semi-transparent overlay (rgba(0,0,0,0.3)). Click dismisses drawer.

**Accessibility:** Focus trapped in drawer when open. Focus restored to trigger on close. Escape closes.

**Do:** Use for mobile navigation or dense filter panels · Trap focus · Close on backdrop click

**Don't:** Use for primary desktop navigation (use TopAppBar) · Leave open on navigation · Forget focus trapping

**Responsive:** Full-width overlay on mobile (<600px), 280px panel on tablet+. Backdrop always visible when open.

**Token Values:**
| Token | Value |
|-------|-------|
| --drawer-width | 280px |
| --drawer-bg | `#ffffff` |
| --drawer-shadow | `var(--shadow-xl)` |
| --drawer-backdrop | `rgba(0,0,0,0.3)` |
| --drawer-transition | `var(--transition-modal)` |
| --drawer-z-index | `var(--z-modal-backdrop)` |

**Composition:** Backdrop + Panel (Header + Close button + Link list + optional Footer). Outside of normal document flow.

**Related:** `top-app-bar.md`, `modal.md`, `link.md`, `icon.md`

## Visual Design

### Appearance
- **Panel:** `#ffffff` bg, 280px width, `--shadow-xl`, full height
- **Backdrop:** `rgba(0,0,0,0.3)`, click to dismiss
- **Header:** 64px, matches top-app-bar height. Close button (28px ghost, right)
- **Links:** `--font-label-md`, full-width, padding 12px 16px, `--color-slate-600`
- **Active link:** `--color-primary-50` bg, `--color-primary` text, 3px left border

### Animation
| Phase | Panel | Backdrop | Duration |
|-------|-------|----------|----------|
| Open | Slide left: translateX(-100%→0) | Fade in 0→1 | 200ms ease-out |
| Close | Slide right: translateX(0→-100%) | Fade out 1→0 | 200ms ease-in |

### Nested Sections
- Collapsible headers: `--font-label-md`, padding 12px 16px, chevron 20px right
- Expanded: chevron ↓, items visible. Collapsed: chevron →, items hidden
- Nested items: indented 16px from parent

### Spacing
- Link padding: 12px 16px
- Link gap: 0 (divider: 1px `--color-slate-100`)
- Section header: same as link + chevron 20px right

### Responsive
`< --bp-mobile`: Full-width panel (not 280px). No backdrop margin.
