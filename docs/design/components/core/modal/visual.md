## Visual Design

### Backdrop
- **Background:** `rgba(11, 28, 48, 0.2)`
- **Z-index:** `--z-modal-backdrop` (300)

### Content Panel
- **Background:** `#ffffff`
- **Max-width:** 440px
- **Shadow:** `--shadow-xl` (0 12px 24px rgba(0,0,0,0.1))
- **Radius:** `--radius-xl` (16px)
- **Padding:** 32px
- **Max-height:** 90vh, scrollable

### Anatomy
- Header: Title (`--font-headline-md`) + Close button (28×28px icon-only ghost, top-right)
- Body: scrollable content
- Footer (optional): buttons right-aligned, gap 8px

### Animation
| Phase | Effect | Duration |
|-------|--------|----------|
| Open | Backdrop fade-in + Content slide-up 16px | 200ms ease-out |
| Close | Backdrop fade-out + Content slide-down 16px | 200ms ease-in |

### Responsive
- `> --bp-mobile`: Centered, max 440px
- `< --bp-mobile`: Full-width, 16px margin each side, padding 24px
