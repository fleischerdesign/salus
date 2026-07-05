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
