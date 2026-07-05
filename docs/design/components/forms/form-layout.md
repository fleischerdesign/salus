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

**Related:** `input.md`, `checkbox.md`, `radio-group.md`, `toggle.md`, `btn.md`, `alert.md`

## Visual Design

### Patterns

| Pattern | Direction | Gap | Max Width | Use |
|---------|-----------|-----|-----------|-----|
| `.form-stack` | Vertical | 16px | 100% | Default layout |
| `.form-row` | Horizontal | 16px | 100% | 2-3 related fields |
| `.form-actions` | Horizontal, right-aligned | 8px | 100%, margin-top 8px | Submit + Cancel |
| `.input-group` | Vertical | 4px (label), 4px (hint) | 100% | Each field unit |

### States

| State | Visual |
|-------|--------|
| Default | Form interactive |
| Submitting | Form `pointer-events: none`, submit button loading (spinner + disabled) |
| Error | Alert banner (error variant) above form. Field-level errors with red text |
| Success | Redirect or inline success alert (see `alert.md`) |

### Spacing
| Gap | Value | Context |
|-----|-------|---------|
| Between form groups | 16px | Vertical stack |
| Between inline fields | 16px | Horizontal row |
| Label↔Input | 4px | Every field |
| Input↔Hint/Error | 4px | Every field |
| Form↔Actions | 8px | Above submit bar |

### Responsive
- `.form-row` collapses to vertical stack below `--bp-mobile`
- `.form-actions` buttons become full-width and stack vertically below `--bp-mobile`

### Max-width
Form container: 560px for simple forms (login, settings). Full-width for complex forms (workout planner, admin).
