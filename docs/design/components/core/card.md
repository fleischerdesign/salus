# Card

**Tokens:** `--card-bg`, `--card-border`, `--card-radius`, `--card-padding`, `--card-shadow-hover`, `--card-title-font`, `--card-gap`

**Anatomy:** Optional header (icon + title + action) + Body content

**States:** Default (white bg, 1px slate-200 border, no shadow) · Hover (md shadow, unless overridden)

**Sizes:** One size. Internal padding: `--space-lg` (24px).

**Spacing:** Header↔Body: `--space-md` (16px) · Card↔Card gap: `--space-md`

**Responsive:** Full-width below `bp-mobile`. Grid-based above.

**Do:** Use for content containers · Keep consistent 24px padding · Include header with title for scannability

**Don't:** Nest cards within cards · Vary padding per card instance · Omit header when card needs context
