# Back Link

**Anatomy:** Arrow icon (left) + "Back" label + Optional destination text

**States:** Default · Hover (primary color)

**Appearance:** btn-secondary or inline-link variant. Arrow: `arrow_back` Material Symbol, 18px. Label: body-sm font.

**Usage:** Top-left of page or section. Navigates to parent/previous screen. Not a browser-back — explicit href to known destination.

**Do:** Use for section/flow navigation · Provide explicit href · Place consistently top-left

**Don't:** Use for browser history back (use JS history.back()) · Place without context · Show on root pages

**Accessibility:**
- Use `<a>` with explicit `href` (not `onclick` history.back)
- Arrow icon: `aria-hidden="true"` (decorative)
- `aria-label` on the link if label is just an icon (e.g., `aria-label="Back to Connections"`)

**Related:** `link.md`, `icon.md`, `breadcrumb.md`

## Visual Design

### Appearance
- **Layout:** Arrow icon (18px) + "Back" label + Optional destination text, horizontal row
- **Icon:** 18px `arrow_back`, `--color-slate-500` (default) → `--color-primary` (hover)
- **Label:** `--font-body-sm`, `--color-slate-600` (default) → `--color-primary` (hover)
- **Destination text:** `--font-caption`, `--color-slate-400`, after "Back" label, 4px gap (e.g., "Back to Connections")

### States
| State | Icon Color | Label Color |
|-------|-----------|-------------|
| Default | `--color-slate-500` | `--color-slate-600` |
| Hover | `--color-primary` | `--color-primary` |
| Focus | Standard focus ring | — |

Transition: 150ms ease-default.

### Spacing
- Icon↔Label: 4px
- Label↔Destination: 4px
- Placement: top-left of page/section, 8px above content
