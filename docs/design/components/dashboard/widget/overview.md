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
