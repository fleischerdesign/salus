# Modal

**Tokens:** `--modal-backdrop-bg`, `--modal-backdrop-filter`, `--modal-content-max-width`, `--modal-shadow`, `--modal-radius`, `--modal-animation`

**Anatomy:** Backdrop (semi-transparent overlay) + Content (card within scrollable container)

**States:** Closed · Opening (fade-in + slide-up, 200ms) · Open · Closing

**Sizes:** Max-width 440px. Fluid width below that. Max-height 90vh, scrollable.

**Accessibility (mandatory):**
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby` referencing title
- Focus trapped inside modal while open
- Focus restored to trigger element on close
- Escape key closes modal
- Backdrop click closes modal (unless prevented)

**Do:** Use for focused tasks (forms, confirmations, details) · Always provide close button · Trap focus · Label with title

**Don't:** Open modal from another modal · Omit Escape key handler · Forget focus restoration · Make non-dismissable without explicit reason

**Composition:**
- Contains one Card (for content structure)
- Allowed in card: Form elements, Buttons, Text, Icon, Alert
- Forbidden: Another Modal (no nested modals), Toast (modals are above toasts)

**Responsive:** Full-width with 16px margin on mobile (<600px). Max-width 440px on larger screens. Content scrollable at max-height 90vh.

**Related:** `card.md`, `alert.md`, `confirmation-dialog.md`, `wizard.md`, `focus-ring.md`, `button.md`
