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
