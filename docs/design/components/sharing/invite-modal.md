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

**Related:** `modal.md`, `copy-to-clipboard.md`, `icon.md`, `btn.md`

## Visual Design

### Contents
- **QR Code:** 200×200px, `#ffffff` bg, `--radius-md`, centered, server-generated PNG
- **URL input:** readonly, `--font-code-sm`, `--color-slate-100` bg, full-width, padding 10px 12px, `--radius-md`
- **Copy button:** primary button (or ghost), right of URL input, icon `content_copy` 16px + "Copy"
- **Success feedback:** "Copied!" (check icon 16px, tertiary-600), 2s duration

### States
| State | Copy Button |
|-------|------------|
| Default | "Copy" + icon |
| Hover | Ghost hover |
| Copied (2s) | ✓ "Copied!", `--color-tertiary-600` |
| Error | "Failed", `--color-error-600` |

### Spacing
- QR↔URL: 24px
- URL↔Copy button: 8px
- Modal padding: 32px
