# Input

**Tokens:** `--input-bg`, `--input-border`, `--input-radius`, `--input-padding`, `--input-font`, `--input-focus-border`, `--input-focus-ring`, `--input-error-border`, `--input-label-font`, `--input-label-color`, `--input-hint-color`

**Variants:** Text · Select · Textarea · Color

**Anatomy:** Label (above) + Input + Hint/Error text (below)

**States:** Default (1px slate-300 border) · Focus (primary border + 2px primary-200 ring) · Error (error-400 border, red label) · Disabled (opacity 0.5) · Read-only (no focus ring)

**Sizes:** Standard only. Color input: 44×80px.

**Spacing:** Label↔Input: 4px · Input padding: 10px 12px · Error↔Input: 4px

**Required fields:** Asterisk or "(required)" text. Input HTML `required` attribute. Visual indicator is mandatory.

**Error state:** `aria-describedby` linking input to error span. Error spans MUST be programmatically associated.

**Do:** Always show label above · Use hint for format guidance · Mark required fields visibly · Associate errors with aria-describedby

**Don't:** Placeholder as label replacement · Rely on color alone for error state · Leave errors unassociated from inputs

**Accessibility:**
- Every input MUST have an associated `<label>` with matching `for`/`id`
- Error text linked via `aria-describedby="error-{id}"` on input
- Error container: `role="alert"` for immediate screen reader announcement
- Required fields: `required` attribute + `aria-required="true"` + visual asterisk
- Hint text: `aria-describedby` separate from error
- Native `<input>`/`<select>`/`<textarea>` — no custom `<div>` replacements
- Focus: primary border + ring, never `outline: none` without replacement

**Responsive:** Full-width on mobile. `.form-row` collapses to vertical stack below `bp-mobile`.

## Visual Design

### Appearance
- **Background:** `--color-slate-50`
- **Border:** `1px solid --color-slate-300`
- **Radius:** `--radius-md` (8px)
- **Height:** 44px
- **Padding:** 10px 12px
- **Font:** `--font-body-md`

### Anatomy
- **Label:** above, `--font-label-md`, `--color-on-surface`, gap 4px
- **Input:** the field
- **Hint:** below, `--font-body-sm`, `--color-slate-500`, gap 4px
- **Error:** below, `--font-body-sm`, `--color-error-600`, with error icon 16px
- **Required:** asterisk `*` in `--color-error-500` after label

### States

| State | Border | Background | Other |
|-------|--------|------------|-------|
| Default | `--color-slate-300` | `--color-slate-50` | — |
| Hover | `--color-slate-400` | `--color-slate-50` | — |
| Focus | `--color-primary-500` | `#ffffff` | Ring: `0 0 0 2px --color-primary-200` |
| Error | `--color-error-400` | `--color-error-50` | Error icon right, error text below |
| Disabled | `--color-slate-200` | `--color-slate-100` | Opacity 0.5, cursor not-allowed |
| Read-only | `--color-slate-200` | `--color-slate-50` | No focus ring, cursor default |
| Filled | `--color-slate-300` | `--color-slate-50` | Clear button (×, 20px) right |

### Icon
- Left icon: 20px, `--color-slate-400`, 12px from left
- Right icon / clear: 20px, 12px from right
- With icon: padding adjusts to 38px

### Sizes & Spacing
- One size: 44px height. Textarea: min 88px
- Label↔Input: 4px. Input↔Hint/Error: 4px
- Form row gap: 16px

**Related:** `select.md`, `textarea.md`, `color-picker.md`, `focus-ring.md`, `form-layout.md`, `search-input.md`, `autocomplete.md`, `stepper.md`, `slider.md`, `date-picker.md`
