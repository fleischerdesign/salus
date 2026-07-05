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
