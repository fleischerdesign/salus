# Context Menu

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Trigger element with right-click (or long-press) handler + Floating menu near cursor

**States:** Hidden · Visible (at cursor position, lg shadow, 8px radius, 4px padding) · Dismissed (click outside or Escape)

**Menu items:** 12px horizontal padding, 8px vertical, body-sm font. Hover: slate-50 bg. Separator: 1px slate-200, 4px vertical margin. Destructive items: error-600 text.

**Position:** Auto-flip to stay within viewport. Prefer bottom-right of cursor. Fall back to top-right, bottom-left, etc.

**Accessibility:** Escape closes. Arrow keys navigate items. Enter selects. Focus returns to trigger on close.

**Do:** Use for secondary actions on data rows · Auto-position within viewport · Support keyboard navigation

**Don't:** Show on every element · Use as primary action mechanism · Omit keyboard access
