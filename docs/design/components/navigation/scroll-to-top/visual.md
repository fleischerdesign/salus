## Visual Design

### Appearance
- **Button:** 40×40px circle, `--color-primary` bg, `--shadow-md`, `--radius-full`
- **Icon:** `arrow_upward` Material Symbol, 20px, `#ffffff`, centered
- **Position:** fixed, bottom: 24px, right: 24px
- **Z-index:** `--z-sticky` (200)

### States
| State | Opacity | Shadow | Animation |
|-------|---------|--------|-----------|
| Hidden (< 300px scroll) | 0 (offscreen) | — | — |
| Appearing (> 300px) | 0→1 | `--shadow-md` | Fade-in 200ms ease-out |
| Visible | 1 | `--shadow-md` | — |
| Hover | 1 | `--shadow-lg` | Shadow transition 150ms |
| Disappearing (< 300px) | 1→0 | `--shadow-md` | Fade-out 150ms ease-in |

### Scroll Behavior
`scroll-behavior: smooth`. Scrolls to top of document.

### Spacing
- Bottom offset: 24px
- Right offset: 24px
- Button size: 40×40px, icon: 20px
