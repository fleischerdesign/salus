# Visual Rules — System-Wide Standards

Every component inherits these rules unless explicitly overridden in its spec.

---

## Focus Ring

All interactive elements (buttons, inputs, links, selects, checkboxes, toggles):

- **Width:** 2px
- **Color:** `--color-primary-500` (`#4f46e5`)
- **Offset:** 2px (gap between element edge and ring)
- **Trigger:** `:focus-visible` only (not on mouse click)
- **Transition:** instant (no animation on focus)

Token: `--focus-ring-width`, `--focus-ring-color`, `--focus-ring-offset`

---

## Disabled State

All interactive elements in disabled state:

- **Opacity:** 0.5 (`--disabled-opacity`)
- **Cursor:** `not-allowed` (`--disabled-cursor`)
- **Pointer events:** `pointer-events: none`
- **Focus:** Not focusable (native `disabled` attribute)
- **Visuals:** Element retains its variant colors; only opacity changes

---

## Transitions

All interactive state changes use these defaults:

| Transition | Duration | Easing |
|-----------|----------|--------|
| Background color | `--duration-fast` (150ms) | `--ease-default` |
| Border color | `--duration-fast` (150ms) | `--ease-default` |
| Box shadow | `--duration-fast` (150ms) | `--ease-default` |
| Opacity | `--duration-fast` (150ms) | `--ease-default` |
| Transform (scale/translate) | `--duration-normal` (200ms) | `--ease-out` |
| Color (text) | `--duration-fast` (150ms) | `--ease-default` |
| Show/Hide (opacity+transform) | `--duration-fast` (150ms) | `--ease-out` |

**Show/Hide Rule:** NEVER toggle `display:none` ↔ `display:block` — it breaks CSS transitions. Always use `opacity` + `pointer-events` + `transform`:

```css
/* ❌ WRONG */
.xxx__dropdown { display: none; }
.xxx__trigger[data-open] + .xxx__dropdown { display: block; }

/* ✅ CORRECT */
.xxx__dropdown {
    opacity: 0; pointer-events: none; transform: translateY(-4px);
    transition: opacity var(--duration-fast) var(--ease-out),
                transform var(--duration-fast) var(--ease-out);
}
.xxx__trigger[data-open] + .xxx__dropdown {
    opacity: 1; pointer-events: auto; transform: translateY(0);
}
```

---

## Iconography

- **Library:** Material Symbols (Google Fonts, Rounded style)
- **Class:** `.material-symbols-outlined`
- **Weight:** 400 (default)
- **Fill:** 0 (outlined)
- **Grade:** 0 (default optical size)
- **Optical Size:** 20px for icons ≤20px, 24px for icons >20px, 48px for 40-48px icons

Icon sizes: 16px · 18px · 20px · 22px · 24px · 40px · 48px

---

## Typography Assignment

Which font style to use for which UI element role:

| Role | Token | Weight | Size | Line |
|------|-------|--------|------|------|
| Page title | `--font-headline-lg` | 700 | 28px | 36px |
| Widget title | `--font-headline-md` | 600 | 20px | 28px |
| Card header | `--font-headline-md` | 600 | 20px | 28px |
| Body text | `--font-body-md` | 400 | 16px | 24px |
| Secondary text | `--font-body-sm` | 400 | 14px | 20px |
| Button label | `--font-label-md` | 600 | 13px | 18px |
| Form label | `--font-label-md` | 600 | 13px | 18px |
| Navigation link | `--font-label-md` | 600 | 13px | 18px |
| Badge / Chip | `--font-label-sm` | 500 | 12px | 16px |
| Table header | `--font-label-sm` | 500 | 12px | 16px |
| Table cell | `--font-body-sm` | 400 | 14px | 20px |
| Axis label | `--font-caption` | 400 | 11px | 16px |
| Timestamp | `--font-caption` | 400 | 11px | 16px |
| Code / monospace | `--font-code-sm` | 400 | 13px | 20px |

---

## Elevation

| Level | Shadow | Z-Index | Used For |
|-------|--------|---------|----------|
| 0 (Ground) | None | 0 | Body, text, inline elements |
| 1 (Raised) | `--shadow-sm` | — | Cards (default) |
| 2 (Overlay) | `--shadow-md` | `--z-dropdown` (100) | Dropdowns, autocomplete, tooltips |
| 3 (Modal) | `--shadow-xl` | `--z-modal` (400) | Modals, drawers |
| 4 (Top) | None | `--z-tooltip` (500) | Toast notifications, cookie consent |
| Sticky | None | `--z-sticky` (200) | Top app bar, sticky headers |

---

## Spacing Grid

All spacing values are multiples of `--space-unit` (4px):

| Token | Value | Use |
|-------|-------|-----|
| `--space-xs` | 4px | Icon↔Label, chip gap, small gaps |
| `--space-sm` | 8px | Button group gap, card↔card gap, inline gaps |
| `--space-md` | 16px | Section padding, form row gap, header↔body |
| `--space-lg` | 24px | Card padding, page section spacing |
| `--space-xl` | 32px | Page margins (desktop), large section gaps |
| `--space-2xl` | 40px | Very large gaps |
| `--space-3xl` | 48px | Hero sections |
| `--space-4xl` | 64px | Max spacing |

---

## Breakpoints

| Token | Value | Behavior |
|-------|-------|----------|
| `--bp-mobile` | 600px | Single column, full-width elements, stacked nav, hamburger menu |
| `--bp-tablet` | 1024px | Sidebar visible, multi-column grid, desktop nav |

Content max-width: `--space-container-max` = 1440px. Fluid below that.

---

## Semantic Color Usage

| Meaning | Color | Usage |
|---------|-------|-------|
| Positive / Success / Normal | `--color-tertiary` (Emerald) | Success state, in-range, goal met, normal vitals |
| Warning / Caution / Elevated | `--color-warning` (Amber) | Warning state, borderline, attention needed |
| Negative / Error / Critical | `--color-error` (Red) | Error state, critical, abnormal, danger |
| Informational / Neutral | `--color-secondary` (Sky Blue) | Info state, context, hints |
| Brand / Action / Primary | `--color-primary` (Indigo) | CTAs, active states, brand elements, focus |
| Structure / Inactive | `--color-slate` (Slate) | Borders, dividers, disabled backgrounds, placeholders |

---

## Responsive Behavior Rules

| Breakpoint | Modal | Card | Button | Form | Nav |
|-----------|-------|------|--------|------|-----|
| >1024px | Centered, max 440px | Grid layout, normal padding | Inline, normal size | Inline row layout | Horizontal, full top-app-bar |
| 600-1024px | Centered, max 440px | Grid layout | Inline | Inline row | Horizontal, top-app-bar |
| <600px | Full-width, 16px margin | Full-width, stacked | Full-width, stacked vertically | Full-width, stacked | Hamburger menu, mobile nav |

---

## Interaction Feedback

| Action | Visual Response | Duration |
|--------|----------------|----------|
| Hover | Background/border change (component-defined) | 150ms ease-default |
| Press (active) | Slight scale-down or brightness reduction | instant |
| Focus | Standard focus ring | instant |
| Success flash | Brief green background pulse | 600ms |
| Error shake | Horizontal shake | 400ms |
| Content load | Skeleton pulse | 1.8s loop |
| Spinner | Continuous rotation | 800ms per revolution |
| Show/Hide (dropdown, modal) | Opacity fade + vertical slide | 150ms ease-out |
