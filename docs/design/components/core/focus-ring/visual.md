## Visual Design

### Appearance
- **Ring:** `2px solid --color-primary-500`, `2px` offset from element edge
- **Trigger:** `:focus-visible` only — keyboard focus, not mouse click
- **Contrast:** Minimum 3:1 against background

### Element-specific overrides
| Element | Focus Style |
|---------|------------|
| Button, Link, Tab, Checkbox | Standard ring (outline) |
| Input, Select, Textarea | Border color change + `box-shadow: 0 0 0 2px --color-primary-200` |
| Toggle, Slider | Ring on interactive element |

### Rule
Never `outline: none` without a visible replacement. Use `:focus-visible`, not `:focus`.
