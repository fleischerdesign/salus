# Inline Code

**Anatomy:** Monospace text within inline or block context

**States:** Default · Hover (subtle bg change if copyable) · Copied (success feedback if copyable)

**Variants:**
- Inline: `<code>` within text. Padding: 2px 6px, slate-100 bg, slate-700 text, rounded-sm, 13px mono font. For API tokens, variable names, file paths.
- Block: `<pre><code>`. Full-width, padding: 12px 16px, slate-100 bg, rounded-md. For multiline code, JSON, config snippets.

**Token values:** Mono font, body-sm size, compact background.

**Copyable:** Block variant with copy-to-clipboard button (see `copy-to-clipboard.md`).

**Do:** Use mono font · Distinguish from body text with bg · Keep inline code compact

**Don't:** Use for long text (use block variant) · Omit word-break for long tokens · Use sans-serif font

**Accessibility:**
- `<code>` element for inline, `<pre><code>` for block
- Screen readers may announce "code" context — avoid if unnecessary
- Token values: `aria-label` for copyable context (e.g., "API token value")

**Related:** `copy-to-clipboard.md`, `stat.md`
