# Accordion

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Header bar (clickable) + Collapsible content panel

**States:** Collapsed (chevron right, content hidden) · Expanded (chevron down, content visible) · Disabled (cannot expand)

**Header:** Full-width, padding 12px 16px, body-md font, cursor pointer, slate-200 border-bottom. Chevron icon: 20px, slate-500, transition: 200ms rotate.

**Content:** Padding 16px. Slide-down animation (200ms ease-out). No border-bottom on last expanded item.

**Group:** Multiple accordion items stacked. Only one expanded at a time (default) or multiple (configurable).

**Do:** Use for progressive disclosure · Animate expand/collapse · Show chevron direction clearly

**Don't:** Use for single item (use card) · Omit animation (jarring) · Hide critical information (put in expanded by default)
