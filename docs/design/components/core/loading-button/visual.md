## Visual Design

### States

| State | Label | Icon/Spinner | Button State |
|-------|-------|-------------|-------------|
| Default | Visible | None | Active |
| Loading | Hidden (text preserved for width) | Spinner 16px, centered | Disabled, `aria-busy="true"` |
| Success | "Saved!" (2s) | ✓ check 16px, `--color-tertiary-600` | Normal |
| Error | "Failed" (2s) | ✕ 16px, `--color-error-600` | Normal |

### Width Preservation
Text set to `visibility: hidden` (not `display: none`) to prevent layout shift. Spinner absolutely centered.

### Transitions
- Default→Loading: 150ms text fade out + spinner fade in
- Loading→Success: 150ms spinner fade out + check fade in
- Success→Default: 2s delay, then 150ms revert
