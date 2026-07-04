# Form Layout

**Anatomy:** Input groups stacked vertically with consistent spacing.

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
