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

**Related:** `button.md`, `icon.md`
