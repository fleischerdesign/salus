# Confirmation Dialog

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Modal + Icon (warning, 48px) + Title + Description + Primary action button + Cancel button

**States:** Closed · Opening · Open · Confirming (primary button shows loading) · Closed (after confirm)

**Variants:** Danger (error icon + red primary button) · Warning (warning icon + amber button) · Info (info icon + primary button)

**Action:** Primary button executes the destructive/confirming action. Cancel dismisses without action.

**Implementation:** Replaces browser native `confirm()` (hx-confirm fallback). Custom modal with HTMX integration. `hx-confirm` triggers this instead of browser dialog.

**Do:** Use for destructive actions (delete, revoke, disband) · Show icon indicating severity · Provide clear Cancel

**Don't:** Use for non-destructive actions · Omit severity icon · Use generic "Are you sure?" without context
