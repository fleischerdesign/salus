# Invite Modal

**Anatomy:** Modal + QR code image + Copyable invite link + Copy button

**States:** Default · Copied (check icon feedback, 2s) · Copy error (alert icon)

**QR code:** 200×200px, white background, rounded-md. Generated server-side via `/sharing/connections/invite-qr?url=...`

**Link input:** Read-only text input with full URL. Click selects all text. Copy button copies to clipboard.

**Copy feedback:** Button label changes to "Copied!" for 2s.

**Do:** Show QR code for mobile scanning · Provide copyable link · Use server-side QR generation

**Don't:** Use external QR service (privacy) · Omit copy feedback · Show modal without close button

**Responsive:** Modal max-width 440px, full-width with margin on mobile. QR code scales down proportionally.

**Accessibility:**
- QR code image: `alt="QR code invitation link — scan to connect"`
- Copy button: `aria-label="Copy invitation link to clipboard"`
- Link input: `readonly`, `aria-label="Invitation link"`
- Feedback: `aria-live="polite"` announces "Link copied" on success

**Composition:** Modal containing: QR code image + Readonly link input + Copy button + Close button. Loaded via HTMX into modal container.

**Related:** `modal.md`, `copy-to-clipboard.md`, `icon.md`, `button.md`
