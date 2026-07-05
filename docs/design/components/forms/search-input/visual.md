## Visual Design

### Appearance
- **Input:** matches standard Input (44px, slate-50 bg, slate-300 border, rounded-md)
- **Search icon:** 20px, `--color-slate-400`, positioned 12px from left
- **Clear button:** 20px × icon, `--color-slate-400`, positioned 12px from right, appears when text present
- **No results message:** `--font-body-sm`, `--color-slate-400`, centered, padding 16px

### States

| State | Icon (left) | Right Element | Border |
|-------|------------|---------------|--------|
| Empty | Search icon | none | `--color-slate-300` |
| Typing | Search icon | Clear × button | `--color-slate-300` |
| Searching | Spinner 16px replaces icon | Clear × | `--color-slate-300` |
| Focus | Search icon | Clear × (if text) | `--color-primary-500` + ring |
| No results | Search icon | Clear × | `--color-slate-300` |

### Search icon ↔ spinner transition
- When searching: search icon fades out → spinner fades in (150ms)
- When results load: spinner fades out → search icon fades in (150ms)

### Spacing
- Left padding: 38px (icon space: 12px + 20px + 6px)
- Right padding: 38px (clear button space)
- Input padding (no icon zone): 10px top/bottom
