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
