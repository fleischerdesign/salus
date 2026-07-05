## Visual Design

### Appearance
- **Track (off):** `--color-slate-200`, 44×24px, `--radius-full`
- **Track (on):** `--color-primary`
- **Thumb:** `#ffffff`, 20×20px circle, `--shadow-sm`
- **Thumb position (off):** 2px from left. **(on):** 22px from left
- **Label:** `--font-body-md`, gap 12px

### States

| State | Track | Thumb Position |
|-------|-------|---------------|
| Off | `--color-slate-200` | left (2px) |
| Off hover | `--color-slate-300` | left (2px) |
| On | `--color-primary` | right (22px) |
| On hover | `--color-primary-600` | right (22px) |
| Focus | Standard focus ring | — |
| Disabled | inherit + opacity 0.5 | current |

Transition: 150ms ease-default thumb position + track color.

### Sizes
| Size | Track | Thumb | Font |
|------|-------|-------|------|
| Standard | 44×24px | 20×20px | `--font-body-md` |
| Small | 32×18px | 14×14px | `--font-body-sm` |
