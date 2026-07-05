# Scroll to Top

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Floating circular button (40px, shadow-md, primary bg, white arrow-up icon) — bottom-right corner of viewport

**States:** Hidden (near top of page) · Visible (scrolled >300px down, fade-in) · Hover (shadow-lg, brightness 0.9)

**Position:** Fixed, bottom: 24px, right: 24px, z-sticky (200).

**Animation:** Fade-in 200ms when appearing, fade-out 150ms when scrolling back to top. Scroll behavior: smooth.

**Do:** Show only after scrolling · Use smooth scroll · Position bottom-right consistently

**Don't:** Show at top of page · Obscure content · Use jarring instant scroll

**Accessibility:**
- Button: `aria-label="Scroll to top"`
- Icon: `aria-hidden="true"`
- Keyboard: focusable in tab order, Enter/Space activates
- Scroll behavior: `scroll-behavior: smooth` on `window.scrollTo({top: 0})`

**Token Values:**
| Token | Value |
|-------|-------|
| --scroll-top-size | 40px |
| --scroll-top-bg | `{colors.primary}` |
| --scroll-top-icon-color | `#ffffff` |
| --scroll-top-shadow | `var(--shadow-md)` |
| --scroll-top-offset | 24px |
| --scroll-top-z-index | `var(--z-sticky)` |
| --scroll-top-threshold | 300px |

**Related:** `btn.md`, `icon.md`

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
