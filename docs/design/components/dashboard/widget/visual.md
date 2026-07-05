## Visual Design

### Chrome (Edit Mode)
- **Background:** `--color-slate-50`, `1px solid --color-slate-200` border
- **Drag handle:** 6 dots pattern (drag_indicator icon 20px, `--color-slate-400`, hover: `--color-slate-600`), top-left, cursor: grab
- **Title:** `--font-headline-md`, left-aligned, `--color-on-surface`
- **Action buttons:** 28×28px ghost icon buttons (edit ✎ / delete ✕), right-aligned, gap 4px

### Chrome (Default)
- **Background:** `#ffffff`, card border, no drag handle visible, no action buttons visible
- **Hover:** `--shadow-sm` appears

### Drag Ghost
- **Border:** `2px dashed --color-primary`
- **Opacity:** 0.4
- **Background:** `--color-primary-50`

### Sizes
| Size | Grid Span | Min Height |
|------|-----------|------------|
| Small | 1 column | 120px |
| Medium | 2 columns | 160px |
| Large | 4 columns | 200px |

4-column grid, 16px gap between widgets.

### Delta Indicator
- Positive: `--color-tertiary-600` + ↑ arrow, `--font-label-sm`
- Negative: `--color-error-600` + ↓ arrow, `--font-label-sm`

### Responsive
`< --bp-mobile`: All sizes → 1 column. Edit mode hidden. Touch drag via SortableJS handles.
