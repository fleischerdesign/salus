# Checkbox

**Anatomy:** Input (hidden/visual checkbox) + Label

**States:** Unchecked · Checked · Indeterminate · Disabled

Control: HTML `<input type="checkbox">` with visible label. Wrapped in clickable label for larger touch target.

Inline checkboxes: horizontal row, gap 16px. Stack checkboxes: vertical list, gap 8px.

**Do:** Use for multi-select · Label describes the option · Group related checkboxes visually

**Don't:** Use for single binary choice where Toggle fits better · Place without a label

**Accessibility:**
- Native `<input type="checkbox">` inside `<label>` (implicit) or with matching `for`/`id` (explicit)
- Group label via `<fieldset>` + `<legend>` for related checkboxes
- Indeterminate: `checkbox.indeterminate = true` via JS (not a HTML attribute)
- Focus: visible ring on checkbox, navigate with Tab

**Related:** `toggle.md`, `multiselect.md`, `radio-group.md`, `form-layout.md`

## Visual Design

### Appearance
- **Box:** 20×20px, `--radius-sm` (4px)
- **Unchecked:** `#ffffff` bg, `2px solid --color-slate-300`
- **Checked:** `--color-primary-500` bg, white checkmark icon 14px
- **Indeterminate:** `--color-primary-500` bg, white minus icon 14px
- **Label:** `--font-body-md`, `--color-on-surface`, gap 8px from box

### States

| State | Box Bg | Box Border | Icon |
|-------|--------|------------|------|
| Unchecked | `#ffffff` | `--color-slate-300` | hidden |
| Unchecked hover | `#ffffff` | `--color-slate-400` | hidden |
| Checked | `--color-primary-500` | `--color-primary-500` | white ✓ |
| Checked hover | `--color-primary-600` | `--color-primary-600` | white ✓ |
| Indeterminate | `--color-primary-500` | `--color-primary-500` | white − |
| Disabled | `--color-slate-100` | `--color-slate-200` | `--color-slate-400` |
| Focus | Standard focus ring on box | — | — |

Transition: 150ms ease-default on all state changes.

### Spacing
- Box↔Label: 8px
- Vertical stack gap: 8px
- Inline horizontal gap: 16px

### Indeterminate
Set via JS (`checkbox.indeterminate = true`). Used for "select all" when some children selected.
