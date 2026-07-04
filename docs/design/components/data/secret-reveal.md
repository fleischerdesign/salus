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

**Related:** `button.md`, `icon.md`, `input.md`, `spinner.md`
