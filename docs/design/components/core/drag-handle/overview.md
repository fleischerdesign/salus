# Drag Handle

**Anatomy:** 6-dot grip icon (16px, slate-400), vertically centered, cursor: grab

**States:** Default · Hover (slate-600) · Active/dragging (cursor: grabbing, primary-600) · Disabled (opacity 0.3, cursor: default)

**Placement:** Left edge of draggable item. 8px padding. Always visible in edit/reorder mode, hidden otherwise.

**Do:** Use for reorderable lists and widgets · Show only in edit mode · Change cursor to grab

**Don't:** Show when reorder is disabled · Use without visual affordance · Omit cursor change

**Accessibility:**
- `aria-grabbed="true/false"` on the draggable item
- `role="button"` + `tabindex="0"` for keyboard reordering (Arrow keys move item up/down)
- Announce reorder: `aria-live="polite"` region ("Item moved to position 3 of 5")
- Icon: `aria-hidden="true"` (purely decorative)

**Token Values:**
| Token | Value |
|-------|-------|
| --drag-handle-color | `{colors.slate-400}` |
| --drag-handle-hover-color | `{colors.slate-600}` |
| --drag-handle-active-color | `{colors.primary-600}` |

**Related:** `widget.md`, `list-item.md`, `icon.md`
