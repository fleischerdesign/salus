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
