# Brand — Salus Health Intelligence

## Product Identity

**Salus Health Intelligence** is a sophisticated intelligence layer for modern healthcare.
The target audience includes clinicians, health administrators, and data analysts who
require high-density information without cognitive fatigue.

The brand personality is **authoritative yet empathetic**. The UI evokes a sense of
reliability and "calm intelligence" through generous whitespace, subtle tonal layering,
and a restrained use of the primary brand color to highlight actionable insights rather
than decorate the interface.

The design style follows a **Modern Corporate** aesthetic with a lean toward
**Minimalism**. It prioritizes clarity, systematic organization, and a clinical sense
of precision.

## Color Philosophy

The palette is rooted in **Medical Indigo** (`#4f46e5`), which serves as the primary
driver for brand identity and primary actions.

| Role | Family | Purpose |
|------|--------|---------|
| **Primary** | Indigo | Primary buttons, active navigation, key brand touchpoints |
| **Secondary** | Sky Blue | Informational accents, secondary data visualizations |
| **Tertiary / Success** | Emerald | Success states, positive health trends, system-normal indicators |
| **Error** | Red | Errors, destructive actions, negative health indicators |
| **Warning** | Amber | Caution indicators, pending statuses |
| **Neutral** | Slate | Typography, borders, subtle surface variations — a clean, clinical backdrop |

The background remains a crisp white (`#ffffff`) or very light gray (`#f8fafc`) to
ensure maximum readability of medical records and data tables.

See `tokens/colors.md` for the complete 10-step color scales.

## Typography Philosophy

**Manrope** is the exclusive typeface. It was selected for its modern, geometric
construction which retains high legibility in dense data environments.

Headlines use semi-bold and bold weights with slight negative letter-spacing to appear
assertive and structured. Body text utilizes standard weights for long-form medical
reports. Small labels use increased letter-spacing and medium weight to remain legible
even at 12px, particularly in high-density tables and chart axes.

See `tokens/typography.md` for the complete type scale.

## Layout & Spacing

The system uses a **Fixed Grid** model centered on the screen to maintain a structured,
professional dashboard feel across ultra-wide monitors.

- **Top Navigation:** A persistent `TopAppBar` spans the full viewport width.
- **Content Area:** Max-width container of 1440px.
- **Grid:** 12-column system for desktop layouts.
- **Breakpoints:** Mobile (<600px), Tablet (600-1024px), Desktop (>1024px).

Spacing follows a **4px base unit**.

See `tokens/spacing.md` and `patterns/layout.md`.

## Elevation & Depth

Depth is conveyed through **Tonal Layers** and extremely subtle **Ambient Shadows**.

| Level | Description |
|-------|-------------|
| 0 | Background `#f8fafc` — The application canvas |
| 1 | Card surfaces `#ffffff` — 1px border, no shadow |
| 2 | Hover/Active — Soft diffused shadow |
| 3 | Modals — Pronounced shadow |

See `tokens/elevation.md`.

## Shapes

**Rounded** (8px default) corners soften the clinical nature of the product.

- Standard elements: 8px — buttons, inputs, cards
- Large elements: 16px — dashboard containers, modals
- Chips/Tags: Fully rounded (pill-shaped)

See `tokens/elevation.md`.
