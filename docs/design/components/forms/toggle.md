# Toggle / Switch

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Track + Thumb (rounded pill) + optional Label

**States:** Off (slate-200 track, thumb left) · On (primary track, thumb right) · Disabled (opacity 0.5)

**Sizes:** Standard (44×24px track) · Small (32×18px track)

**Transition:** 150ms ease-default for thumb position and track color.

**Accessibility:** `role="switch"`, `aria-checked="true/false"`. Clickable label.

**Do:** Use for binary on/off settings · Show immediate effect (no Save button needed if auto-persist) · Keep label concise

**Don't:** Use for multi-option selection (use checkbox) · Use without label · Require separate Save action

**Accessibility:**
- `role="switch"` with `aria-checked="true/false"`
- Click or Enter/Space toggles state
- Associated label via `for`/`id`
- Immediate state announcement via `aria-live`

**Token Values:**
| Token | Value |
|-------|-------|
| --toggle-track-width | 44px |
| --toggle-track-height | 24px |
| --toggle-track-bg-off | `{colors.slate-200}` |
| --toggle-track-bg-on | `{colors.primary}` |
| --toggle-thumb-size | 20px |
| --toggle-thumb-bg | `#ffffff` |
| --toggle-transition | `var(--duration-fast) var(--ease-default)` |
| --toggle-disabled-opacity | `0.5` |

**Related:** `checkbox.md`, `radio-group.md`, `button.md`
