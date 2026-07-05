# Card

**Tokens:** `--card-bg`, `--card-border`, `--card-radius`, `--card-padding`, `--card-shadow-hover`, `--card-title-font`, `--card-gap`

**Anatomy:** Optional header (icon + title + action) + Body content

**States:** Default (white bg, 1px slate-200 border, no shadow) · Hover (md shadow, unless overridden)

**Sizes:** One size. Internal padding: `--space-lg` (24px).

**Spacing:** Header↔Body: `--space-md` (16px) · Card↔Card gap: `--space-md`

**Responsive:** Full-width below `bp-mobile`. Grid-based above.

**Do:** Use for content containers · Keep consistent 24px padding · Include header with title for scannability

**Don't:** Nest cards within cards · Vary padding per card instance · Omit header when card needs context

**Composition:**
- Allowed children: Text, Link, Button, Icon, Chip, Table, KeyValue, ProgressBar, any Viz component, form elements
- Forbidden children: Modal (use modal's own card), Toast (use overlay), Card (no nesting)
- Max nesting depth: 1 (Card → Body only, no Card → Card → Body)

## Visual Design

### Appearance
- **Background:** `#ffffff`
- **Border:** `1px solid --color-slate-200`
- **Shadow (default):** none (flat)
- **Shadow (hover):** `--shadow-md` (0 4px 12px rgba(0,0,0,0.05))
- **Radius:** `--radius-md` (8px)

### Variants
| Variant | Background | Border | Shadow |
|---------|-----------|--------|--------|
| Default | `#ffffff` | `1px --color-slate-200` | none → hover: `--shadow-md` |
| Elevated | `#ffffff` | `1px --color-slate-200` | `--shadow-sm` by default |
| Outlined | `#ffffff` | `1px --color-slate-200` | none |
| Flat | `--color-slate-50` | none | none |

### Anatomy
- Header (optional): Icon (24px) + Title (`--font-headline-md`) + Action button (right-aligned)
- Body: freeform content
- Footer (optional): action buttons, right-aligned, gap 8px

### Sizes & Spacing
| Property | Value |
|----------|-------|
| Padding | 24px (`--space-lg`) |
| Header↔Body gap | 16px (`--space-md`) |
| Body↔Footer gap | 16px |
| Card↔Card gap | 16px |

### States
| State | Visual | Duration |
|-------|--------|----------|
| Default | White bg, border, no shadow | — |
| Hover | `--shadow-md` appears | 150ms ease-default |
| Clickable card | Cursor pointer, full card interactive | — |

### Responsive
- `< --bp-mobile`: Full-width, padding 16px
- `> --bp-mobile`: Grid layout, padding 24px

**Accessibility:**
- Use `<section>` or `<article>` element for semantic HTML
- If card is clickable as a whole: `tabindex="0"`, `role="button"`, Enter/Space handlers
- Card header title: inside `<h2>`/`<h3>` for heading hierarchy
- Grouped cards: wrap in `<ul>` with each card as `<li>` if they represent a collection

**Related:** `empty-state.md`, `key-value.md`, `compare.md`, `widget.md`
