# Tooltip

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Trigger element + Floating tooltip box (arrow pointing to trigger)

**Placement:** Auto-positioned (top preferred, falls back to bottom/left/right). 8px gap from trigger.

**Appearance:** Slate-800 bg, slate-50 text, body-sm font, 8px padding, 6px border-radius, 1px rgba(255,255,255,0.15) border. 4px arrow pointing to trigger.

**States:** Hidden · Visible (on hover/focus, 150ms delay) · Dismissed (on mouseleave/blur)

**Max width:** 280px. Text wraps.

**Accessibility:** Tooltip content as `aria-describedby` on trigger. Visible on focus (keyboard accessible). Not the only source of critical information.

**Do:** Use for supplementary information · Keep text short · Show on hover AND focus

**Don't:** Put critical information only in tooltip · Use on touch-only devices · Chain tooltips
