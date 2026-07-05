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

**Related:** `stepper.md`, `toggle.md`, `input.md`

## Visual Design

### Appearance
- **Track:** 4px height, `--color-slate-200`, `--radius-full`
- **Fill (left of thumb):** `--color-primary-500`, `--radius-full`
- **Thumb:** 20px circle, `#ffffff` bg, `2px solid --color-primary`, `--shadow-sm`
- **Labels:** `--font-label-sm`, `--color-slate-500`, min left, max right

### States

| State | Thumb Size | Thumb Border | Thumb Shadow | Cursor |
|-------|-----------|-------------|-------------|--------|
| Default | 20px | `2px --color-primary` | `--shadow-sm` | pointer |
| Hover | 24px | `2px --color-primary` | `--shadow-md` | pointer |
| Active (dragging) | 24px | `2px --color-primary-600`, ring `0 0 0 4px --color-primary-200` | `--shadow-md` | grabbing |
| Disabled | 20px | `2px --color-slate-300` | none | not-allowed, opacity 0.5 |

Thumb transition: size 150ms ease-default. Fill transition: width 0ms (instant, follows thumb).

### Variants
| Variant | Thumbs | Ticks | Use |
|---------|--------|-------|-----|
| Single | 1 | No | Numeric input |
| Range | 2 | No | Min/max filter |
| Discrete | 1 or 2 | Yes (at step intervals) | Step-constrained values |

Tick mark: 8px height, 1px `--color-slate-300`, at each step position.

### Spacing
- Track↔Labels: 8px above/below
- Min/max label spacing: labels at track edges
