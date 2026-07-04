# Icon

**Anatomy:** Material Symbols font glyph, sized and colored consistently

**Sizes:** Standard sizes by context:

| Context | Size |
|---------|------|
| Inline with text | 18px |
| Navigation icons | 20px |
| Button icons | 18px |
| Widget icons | 22px |
| Card header icons | 24px |
| Feature/hero icons | 40-48px |
| Empty state icons | 48px |
| Favicon-sized | 16px |

**Colors:** Default: `currentColor` (inherits parent text color). Semantically colored per context (primary, error, success).

**Variants:** Outlined (default) · Filled (`fontVariationSettings: 'FILL' 1`) — used for active/favorite states.

**Accessibility:** `aria-hidden="true"` when purely decorative. `aria-label` when icon is the only interactive element content.

**Do:** Use consistent sizing · Inherit color · Mark decorative icons as aria-hidden · Provide aria-label for icon-only buttons

**Don't:** Mix font sizes in same component · Use icon without text label in interactive elements · Skip accessibility

**Token Values:** Inherits `currentColor` from parent. Size via `font-size`. Filled variant: `fontVariationSettings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24`.

**Related:** `button.md`, `link.md`, `avatar.md`, `status-dot.md`
