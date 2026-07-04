# Motion — Transitions & Breakpoints

## Breakpoints

| Token | Value | Usage |
|-------|-------|-------|
| `bp-mobile` | 600px | Mobile layout |
| `bp-tablet-sm` | 768px | Compact tablet |
| `bp-tablet` | 900px | Tablet layout |
| `bp-desktop` | 1024px | Desktop navigation |

> CSS custom properties don't work inside `@media` queries. Hardcode numeric values in CSS.

## Duration

| Token | Value | Usage |
|-------|-------|-------|
| `duration-instant` | 100ms | Button press |
| `duration-fast` | 150ms | Hover, focus (default) |
| `duration-normal` | 200ms | Modal open/close |
| `duration-slow` | 300ms | Progress bars |
| `duration-very-slow` | 500ms | Chart updates |
| `duration-glacial` | 800ms | Ring chart, skeleton |

## Easing

| Token | Value | Usage |
|-------|-------|-------|
| `ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard Material |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Entering |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Exiting |
| `ease-linear` | `linear` | Spinners |

## Component Transitions

```css
--transition-btn: background var(--duration-fast) var(--ease-default),
                  box-shadow var(--duration-fast) var(--ease-default);
--transition-input: border-color var(--duration-fast) var(--ease-default),
                    box-shadow var(--duration-fast) var(--ease-default);
--transition-modal: opacity var(--duration-normal) var(--ease-out),
                    transform var(--duration-normal) var(--ease-out);
--transition-card: box-shadow var(--duration-fast) var(--ease-default);
```
