# Radio Group

**Tokens:** Reuses `--btn-sm-*` tokens

**Anatomy:** Group label (label-sm) + Option list (horizontal or vertical button-group)

**States:** Default · Selected/Active (btn-sm.active: primary bg, white text, primary border) · Focus

**Implementation:** Hidden radio inputs with visible button labels. Wrapped in form with `onchange`, or HTMX-driven.

**Do:** Use for single-select from small set (2-5 options) · Style as button group for visual clarity · Provide group label

**Don't:** Use for >5 options (use Select) · Use without visible label · Mix horizontal and vertical

**Accessibility:**
- `<fieldset>` + `<legend>` wraps the group
- Each option: `<input type="radio">` + `<label>` with matching `for`/`id`
- Selected: `checked` attribute
- Keyboard: Tab to group, Arrow keys change selection within group

**Token Values:**
| Token | Value |
|-------|-------|
| --radio-group-gap | `8px` |
| --radio-group-item-padding | `6px 12px` |

**Related:** `checkbox.md`, `toggle.md`, `select.md`, `form-layout.md`
