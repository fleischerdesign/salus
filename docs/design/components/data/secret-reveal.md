# Secret Reveal

**Anatomy:** Masked value (```````` or `****`) + Reveal button (eye icon) + Revealed value (inline replacement)

**States:** Masked (default) · Revealing (spinner, 150ms) · Revealed (plain text, eye-off icon to re-hide)

**Interaction:** hx-get to server fetches the actual value. Server enforces authorization. Client replaces masked text with revealed value inline.

**Token references:** Uses `--input-*` tokens for text styling. Reveal button uses `--btn-ghost-*` tokens.

**Security:** Value is NEVER in the HTML source. Fetched on-demand from server, which validates user authorization. Ideal for API tokens, secret keys, passwords in admin interfaces.

**Do:** Use for sensitive config values · Fetch on demand · Show re-hide affordance · Never embed in source

**Don't:** Cache revealed value client-side · Expose via HTML attribute · Use for non-sensitive data

**Accessibility:**
- Reveal button: `aria-expanded="true/false"`, `aria-label="Reveal secret value"` / `"Hide secret value"`
- Masked state: text visually shows ````/`****`, `aria-label="Secret value hidden"`
- Revealed state: `aria-label` describes the revealed value
- Keyboard: Enter/Space toggles reveal

**Token Values:**
| Token | Value |
|-------|-------|
| --secret-mask-char | `*` |
| --secret-mask-length | 12 |
| --secret-reveal-btn-size | 20px |
| --secret-transition | `var(--duration-fast) var(--ease-default)` |

**Related:** `btn.md`, `icon.md`, `input.md`, `spinner.md`

## Visual Design

### States

| State | Display | Button Icon | Button Style |
|-------|---------|------------|-------------|
| Masked | `************` (12 × `*`), `--color-slate-400` | `visibility` (eye), 20px | Ghost, `--color-slate-500` |
| Loading | Masked + spinner 16px in button | Spinner 16px | Ghost, disabled |
| Revealed | Plain text, `--font-code-sm`, `--color-on-surface` | `visibility_off` (eye-off), 20px | Ghost, `--color-primary` |
| Error | Masked + error tooltip | `error` 16px | Ghost, `--color-error-500` |

### Masked Value
- Character: `*` (asterisk)
- Length: 12 (fixed, doesn't reveal actual length)
- Font: `--font-code-sm` (13px, monospace)
- Color: `--color-slate-400`

### Revealed Value
- Font: `--font-code-sm` (13px, monospace)
- Color: `--color-on-surface`
- Background: `--color-slate-50`, padding 4px 8px, `--radius-sm`

### Layout
Value + Button, horizontal row. Gap: 8px. Button: 28×28px icon-only ghost.

### Security
Value NEVER in HTML source. Fetched server-side on click. Server validates authorization.
