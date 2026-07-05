## Visual Design

### Appearance
- **Icon:** `drag_indicator` Material Symbol, 20px, `--color-slate-400`, 6-dot pattern
- **Size:** 20×20px clickable area, 8px padding each side
- **Cursor:** grab (default), grabbing (active)

### States
| State | Icon Color | Cursor |
|-------|-----------|--------|
| Default | `--color-slate-400` | grab |
| Hover | `--color-slate-600` | grab |
| Active (dragging) | `--color-primary-600` | grabbing |
| Disabled | `--color-slate-300`, opacity 0.3 | default |

### Placement
Left edge of draggable item, vertically centered. Visible only in edit/reorder mode.
