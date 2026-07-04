# Toggle / Switch

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Track + Thumb (rounded pill) + optional Label

**States:** Off (slate-200 track, thumb left) · On (primary track, thumb right) · Disabled (opacity 0.5)

**Sizes:** Standard (44×24px track) · Small (32×18px track)

**Transition:** 150ms ease-default for thumb position and track color.

**Accessibility:** `role="switch"`, `aria-checked="true/false"`. Clickable label.

**Do:** Use for binary on/off settings · Show immediate effect (no Save button needed if auto-persist) · Keep label concise

**Don't:** Use for multi-option selection (use checkbox) · Use without label · Require separate Save action
