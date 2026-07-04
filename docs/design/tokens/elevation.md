# Elevation, Radius & Z-Index

## Border Radius

| Token | Value |
|-------|-------|
| `none` | 0 |
| `xs` | 2px |
| `sm` | 4px |
| `md` | 8px |
| `lg` | 12px |
| `xl` | 16px |
| `2xl` | 24px |
| `full` | 9999px |

Default component radii: Buttons/Inputs/Cards → `md`, Chips → `full`, Modals → `xl`.

## Shadows

| Level | Token | Value | Usage |
|-------|-------|-------|-------|
| 0 | `none` | `none` | Flat surfaces |
| 1 | `sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| 2 | `md` | `0 4px 12px rgba(0,0,0,0.05)` | Card hover |
| 3 | `lg` | `0 8px 16px rgba(11,28,48,0.12)` | Dropdowns |
| 4 | `xl` | `0 12px 24px rgba(0,0,0,0.1)` | Modals |

Dark mode: `md` → `rgba(0,0,0,0.3)`, `lg` → `rgba(0,0,0,0.4)`, `xl` → `rgba(0,0,0,0.5)`.

Input focus ring: `0 0 0 2px var(--color-primary-200)`.

## Z-Index

| Token | Value | Usage |
|-------|-------|-------|
| `z-dropdown` | 100 | Dropdowns, popovers |
| `z-sticky` | 200 | Sticky headers |
| `z-modal-backdrop` | 300 | Modal overlay |
| `z-modal` | 400 | Modal content |
| `z-tooltip` | 500 | Tooltips, toasts |
| `z-debug` | 9999 | Debug overlays |
