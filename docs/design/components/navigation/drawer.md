# Drawer

> **Status: Design spec only — not yet implemented.**

**Anatomy:** Slide-out panel (left, 280px) + Backdrop overlay + Close button + Header + Navigation links + Footer

**States:** Closed · Opening (slide-in from left, 200ms ease-out) · Open · Closing

**Contents:** Same as mobile nav but with dedicated close affordance. Can include nested sections with collapsible headers.

**Backdrop:** Semi-transparent overlay (rgba(0,0,0,0.3)). Click dismisses drawer.

**Accessibility:** Focus trapped in drawer when open. Focus restored to trigger on close. Escape closes.

**Do:** Use for mobile navigation or dense filter panels · Trap focus · Close on backdrop click

**Don't:** Use for primary desktop navigation (use TopAppBar) · Leave open on navigation · Forget focus trapping
