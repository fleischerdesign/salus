# Form Layout

**Anatomy:** Input groups stacked vertically with consistent spacing.

**States:** Default · Submitting (form disabled, submit button loading) · Error (alert above form, field-level errors) · Success (redirect or inline success message)

**Tokens:** `--input-*` (see input.md)

**Patterns:**

| Pattern | Class | Use |
|---------|-------|-----|
| Vertical stack | `.form-stack` | Default form layout, 16px gap |
| Horizontal row | `.form-row` | Side-by-side inputs, 16px gap |
| Action bar | `.form-actions` | Submit + Cancel buttons, 16px gap, 8px top margin |
| Input group | `.input-group` | Label + Input + Hint/Error |

**Spacing:** Between groups: 16px · Label↔Input: 4px · Input↔Hint: 4px · Form↔Actions: 8px

**Responsive:** `.form-row` collapses to vertical on mobile.

**Do:** Use form-stack as default · Group related fields in form-row · Place submit button in form-actions

**Don't:** Use form-row for more than 2-3 fields · Put submit outside form-actions · Forget error states

**Accessibility:**
- `<form>` with `action` and `method` for non-JS fallback alongside HTMX attributes
- All inputs: matching `for`/`id` labels, error `aria-describedby`
- Submit button: `type="submit"`, `aria-busy` during submission
- Fieldset grouping for related inputs with `<legend>`

**Composition:** Contains Input/Select/Textarea/Checkbox/Toggle groups stacked vertically or in rows. Submit + Cancel in form-actions.

**Related:** `input.md`, `checkbox.md`, `radio-group.md`, `toggle.md`, `button.md`, `alert.md`
