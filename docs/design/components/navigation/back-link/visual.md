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
