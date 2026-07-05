# Dashboard Widget

**Tokens:** `--card-*` tokens plus `--widget-delta--positive`, `--widget-delta--negative`

**Anatomy:** Chrome (drag handle + title + actions) + Body (viz component), within `.dashboard-widget`

**States:**
- Default: hover shadow, drag handle hidden, actions hidden
- Edit mode: chrome has slate-50 bg + border, drag handle + actions visible
- Drag ghost (SortableJS): dashed primary border, 0.4 opacity

**Sizes:** Small (span 1) · Medium (span 2) · Large (span 4). 4-column dashboard grid.

**Viz routing:** Widget body delegates to viz template based on `widget.viz_type`. Each viz implements its own small/medium/large rendering.

**Delta indicator:** Positive (success) or negative (error) with arrow icon. Displayed in widget body.

**Do:** Use consistent chrome for all widgets · Support drag-and-drop reorder · Show delta for trends

**Don't:** Vary chrome across widgets · Forget empty state per widget · Hardcode viz colors (use component tokens)

**Accessibility:**
- Widget container: `role="region"` with `aria-label` from widget title
- Edit mode: drag handle has `aria-grabbed`, keyboard reorder via Arrow keys
- Widget chrome buttons: each has distinct `aria-label` ("Edit widget", "Delete widget", "Drag to reorder")
- Empty widget: renders empty-state component with descriptive message
- Auto-refresh via HTMX: `aria-live="polite"` on widget body

**Composition:** Chrome (DragHandle + Title + Action buttons) + Body (Viz component or EmptyState). Inside dashboard-grid container.

**Responsive:** Widgets collapse to single column on mobile (<600px). Small/Medium/Large all span 1 column. Edit mode hidden on mobile (touch drag via SortableJS handles reorder).

**Related:** `drag-handle.md`, `viz-*.md`, `empty-state.md`, `btn.md`, `icon.md`, `kpi-card.md`

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
