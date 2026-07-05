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

## Visual Design

### Appearance
- **Container:** vertical list, no border-top, 1px `--color-slate-200` border-bottom per item
- **Padding:** 12px 16px (standard), 8px 12px (compact)
- **Icon (optional):** 20px, left, `--color-slate-400`, gap 12px to content
- **Primary text:** `--font-body-md`, `--color-on-surface`
- **Secondary text:** `--font-body-sm`, `--color-slate-500`, below primary, 2px gap
- **Action (optional):** icon button (28×28px ghost), right-aligned

### Variants

| Variant | Padding | Font |
|---------|---------|------|
| Standard | 12px 16px | `--font-body-md` |
| Compact | 8px 12px | `--font-body-sm` |
| With actions | 12px 16px + right actions | `--font-body-md` |
| With metadata | 12px 16px + secondary line | `--font-body-md` + `--font-body-sm` |

### States

| State | Background |
|-------|-----------|
| Default | `#ffffff` |
| Hover | `--color-slate-50` |
| Active/Selected | `--color-primary-50` |
| Disabled | opacity 0.5, cursor not-allowed |

### Spacing
- Icon↔Content: 12px
- Primary↔Secondary text: 2px
- Action↔Content: 16px
- Item↔Item: 0px (border-bottom separates)
