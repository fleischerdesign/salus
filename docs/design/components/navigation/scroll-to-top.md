# Scroll to Top

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Floating circular button (40px, shadow-md, primary bg, white arrow-up icon) — bottom-right corner of viewport

**States:** Hidden (near top of page) · Visible (scrolled >300px down, fade-in) · Hover (shadow-lg, brightness 0.9)

**Position:** Fixed, bottom: 24px, right: 24px, z-sticky (200).

**Animation:** Fade-in 200ms when appearing, fade-out 150ms when scrolling back to top. Scroll behavior: smooth.

**Do:** Show only after scrolling · Use smooth scroll · Position bottom-right consistently

**Don't:** Show at top of page · Obscure content · Use jarring instant scroll
