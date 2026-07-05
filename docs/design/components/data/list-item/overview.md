# List / List Item

**Anatomy:** Row within a vertical list container. Icon (optional) + Content + Action (optional)

**States:** Default · Hover (slate-50 bg) · Active/Selected (primary-50 bg) · Disabled (opacity 0.5)

**Variants:**
- Standard: `padding: 12px 16px`, body-md font
- Compact: `padding: 8px 12px`, body-sm font
- With actions: trailing button or icon (edit/delete)
- With metadata: secondary text below primary content (muted, body-sm)

**Spacing:** 0px between items (border-bottom separation). 1px slate-200 border-bottom.

**Do:** Use for homogeneous item collections · Maintain consistent row height · Show hover feedback

**Don't:** Use for layout (use CSS grid) · Vary row heights in same list · Omit hover state for clickable items

**Accessibility:**
- Use `<ul>` or `<ol>` with `<li>` elements
- Interactive items: `<button>` or `<a>` inside `<li>`, not `onclick` on `<li>`
- Metadata/secondary text: `aria-describedby` linking to primary content
- Actions: icon buttons with `aria-label` per action

**Related:** `table.md`, `chip-row.md`, `context-menu.md`, `drag-handle.md`, `timeline.md`
