# Link

**Anatomy:** Inline text with optional icon

**States:** Default (inherit color, no underline) · Hover (color changes, no underline by default) · Focus (outline/ring for accessibility) · Visited · Active · External (with external-link icon)

**Variants:**
- Navigation link: label-md, slate-600 → primary on hover, 2px primary border-bottom when active
- Inline text link: body-md, primary color, underline on hover, in running text
- Action link: like button-ghost but inline, for "Edit", "View all", "Learn more"

**Accessibility:** Focus visible ring. Distinguishable from regular text by color (NOT by color alone — also font-weight or underline on hover). External links: `rel="noopener noreferrer"`.

**Do:** Use primary color for clickable links · Show underline on hover · Distinguish from body text · Add external icon for off-site links

**Don't:** Use color alone to indicate link · Make link text generic ("click here") · Omit focus styles

**Responsive:** Inline links follow text flow. Navigation links collapse per navigation responsive rules. External link icon always visible regardless of viewport.

**Related:** `btn.md`, `icon.md`, `focus-ring.md`, `back-link.md`, `top-app-bar.md`

## Visual Design

### Variants

| Variant | Font | Default Color | Hover Color | Underline | Context |
|---------|------|--------------|-------------|-----------|---------|
| Inline text | inherit body | `--color-primary` | `--color-primary-600` | On hover | Running text |
| Navigation | `--font-label-md` | `--color-slate-600` | `--color-primary` | Never | Top nav, sidebar |
| Active nav | `--font-label-md` | `--color-primary` | — | 2px solid primary bottom | Current page |
| Action | `--font-label-md` | `--color-primary` | `--color-primary-600` | Never | "Edit", "View all" |

### States

| State | Visual |
|-------|--------|
| Default | Variant color, no underline (except inline on hover) |
| Hover | Color shift + underline (inline), 150ms ease-default |
| Focus | Standard focus ring |
| Active | `--color-primary` + 2px bottom border (nav only) |
| External | Icon 12px after text, `rel="noopener noreferrer"` |
| Disabled | Opacity 0.5, cursor not-allowed |

### Spacing
- External icon gap: 4px after text
- Nav link padding: 12px 16px (top-app-bar), 8px 16px (sidebar)
