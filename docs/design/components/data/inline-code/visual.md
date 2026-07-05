## Visual Design

### Variants

| Variant | Padding | Background | Text Color | Radius | Font |
|---------|---------|-----------|------------|--------|------|
| Inline | 2px 6px | `--color-slate-100` | `--color-slate-700` | `--radius-sm` (4px) | `--font-code-sm` (1`3px) |
| Block | 12px 16px | `--color-slate-100` | `--color-slate-700` | `--radius-md` (8px) | `--font-code-sm` (13px) |

### Inline `<code>`
- Within text, 2px 6px padding, `--color-slate-100` bg, `--radius-sm`
- Word-break: break-all for long tokens
- Use: API tokens, variable names, file paths

### Block `<pre><code>`
- Full-width, 12px 16px padding, `--color-slate-100` bg, `--radius-md`
- Overflow: auto scroll for long lines
- Copy button (optional): top-right, 28×28px ghost, see `copy-to-clipboard.md`

### Spacing
- Inline: 2px 6px
- Block: 12px 16px
- Block margins: 16px above/below when standalone
