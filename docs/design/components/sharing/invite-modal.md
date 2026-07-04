# Invite Modal

**Anatomy:** Modal + QR code image + Copyable invite link + Copy button

**QR code:** 200×200px, white background, rounded-md. Generated server-side via `/sharing/connections/invite-qr?url=...`

**Link input:** Read-only text input with full URL. Click selects all text. Copy button copies to clipboard.

**Copy feedback:** Button label changes to "Copied!" for 2s.

**Do:** Show QR code for mobile scanning · Provide copyable link · Use server-side QR generation

**Don't:** Use external QR service (privacy) · Omit copy feedback · Show modal without close button
