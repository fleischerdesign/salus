# Slider / Range

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Track (horizontal bar) + Thumb(s) (draggable circle) + Optional labels (min/max/current) + Optional tick marks

**States:** Default · Hover (thumb scales to 24px) · Active/dragging (thumb: 24px, primary ring) · Disabled (opacity 0.5)

**Variants:**
- Single value: one thumb. For numeric input, satisfaction rating, pain scale (0-10).
- Range: two thumbs (min + max). For date ranges, value filters.
- Discrete: ticks at defined steps. Snaps thumb to nearest tick.
- Continuous: smooth sliding, no ticks.

**Track:** 4px height, slate-200 bg, rounded-full. Filled portion (left of thumb): primary-500.

**Thumb:** 20px circle, white bg, primary border (2px), shadow-sm. Cursor: grab (default), grabbing (active).

**Accessibility:** `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`. Arrow keys adjust value.

**Do:** Show current value label · Use for range input · Support keyboard · Show min/max labels

**Don't:** Use for binary choices (use toggle) · Omit value feedback · Forget keyboard accessibility

**Accessibility:**
- `role="slider"` on thumb element
- `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, `aria-valuetext`
- Range variant: `aria-valuemin`/`max` on container, `aria-valuenow` on each thumb
- Keyboard: Arrow Left/Down decreases, Arrow Right/Up increases, Home/End to min/max
- Current value label: `aria-live="polite"` for live updates

**Token Values:**
| Token | Value |
|-------|-------|
| --slider-track-height | 4px |
| --slider-track-bg | `{colors.slate-200}` |
| --slider-fill-bg | `{colors.primary-500}` |
| --slider-thumb-size | 20px |
| --slider-thumb-border | `2px solid {colors.primary}` |
| --slider-thumb-bg | `#ffffff` |
| --slider-thumb-shadow | `var(--shadow-sm)` |

**Related:** `number-stepper.md`, `toggle.md`, `input.md`
