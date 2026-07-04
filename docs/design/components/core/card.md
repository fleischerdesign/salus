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

**Accessibility:**
- Use `<section>` or `<article>` element for semantic HTML
- If card is clickable as a whole: `tabindex="0"`, `role="button"`, Enter/Space handlers
- Card header title: inside `<h2>`/`<h3>` for heading hierarchy
- Grouped cards: wrap in `<ul>` with each card as `<li>` if they represent a collection

**Related:** `empty-state.md`, `key-value.md`, `compare.md`, `widget.md`
