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
