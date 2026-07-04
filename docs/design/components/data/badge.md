# Badge (Notification Count)

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Small circle/dot with numeric count, absolutely positioned on the corner of a parent element (avatar, icon, nav link)

**States:** Hidden (count is 0) · Visible (count > 0) · Overflow ("99+" when count > 99)

**Sizes:** Small dot (8px, count not shown — presence only) · Standard (18px, 1-2 digit count)

**Appearance:** Error-500 background, on-error text, label-sm font (10px). Rounded-full. No padding (centered text).

**Position:** Top-right corner of parent, -4px offset (overlaps parent edge). Parent must have `position: relative`.

**Animation:** Scale-in on appear (150ms ease-out). No animation on count change (jarring when numbers rapidly change).

**Do:** Use for notification counts, unread indicators · Show "99+" for overflow · Absolute position on parent

**Don't:** Use as a status indicator (use Chip) · Animate count changes · Show for zero count · Use without parent position:relative
