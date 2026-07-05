## Visual Design

### Appearance
- **Type:** CSS-only rotating ring (`border` + `border-top: transparent` trick)
- **Color:** `--color-primary`
- **Animation:** 0.8s linear infinite rotation (`--spinner-duration`)

### Sizes

| Size | Diameter | Border Width | Context |
|------|----------|-------------|---------|
| SM | 16px | 2px | Inline text, input indicators |
| MD | 24px | 3px | Button loading, card loading |
| LG | 40px | 4px | Full-page, empty container |

### States
| State | Visual |
|-------|--------|
| Hidden | `display: none` |
| Spinning | Visible, rotating, `aria-busy="true"` on parent |
| Stopped | Removed from DOM, content replaces |

### Prefers-reduced-motion
If user prefers reduced motion: spinner stops rotating, shows static ring instead.
