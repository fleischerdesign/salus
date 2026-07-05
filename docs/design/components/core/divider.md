# Divider / Separator

**Anatomy:** Horizontal line with optional centered label text

**States:** Default · With label (line — text — line)

**Appearance:** 1px height, slate-200 background (light), slate-700 (dark). Full width of container.

**With label:** Label centered between two lines. Lines: flex-1, 1px, slate-200. Label: label-sm, slate-400. Gap: 16px.

**Vertical variant:** 1px width, full height of container. Used for side-by-side sections.

**Spacing:** 24px margin above and below in auth forms. 4px in nav/compact contexts.

**Do:** Use for visual separation between sections · Add label when context needs clarification

**Don't:** Overuse — prefer whitespace for separation · Use without semantic purpose

**Accessibility:**
- Use `<hr>` element for horizontal dividers (semantic HTML)
- Decorative dividers: `aria-hidden="true"`
- Labeled dividers: label text is visible and read by screen readers
- Vertical dividers: `aria-hidden="true"` (purely visual separation, not semantic content)

**Related:** `auth-form.md`

## Visual Design

### Appearance
- **Horizontal:** 1px height, `--color-slate-200`, full width
- **Vertical:** 1px width, `--color-slate-200`, full height
- **Dark mode:** `--color-slate-700`

### With Label
Layout: Line (`flex: 1`) — Label — Line (`flex: 1`), gap 16px.
Label: `--font-label-sm`, `--color-slate-400`, centered, no-wrap.

### Spacing
| Context | Margin Above | Margin Below |
|---------|-------------|-------------|
| Auth forms | 24px | 24px |
| Page sections | 32px | 32px |
| Compact (nav) | 4px | 4px |
| Card body | 16px | 16px |

### Responsive
Horizontal: always full-width. Vertical: hidden below `--bp-mobile`.
