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
