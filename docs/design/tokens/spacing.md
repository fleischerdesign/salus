# Spacing

4px base unit. All layout mathematically aligned.

## Scale

| Token | Value | Use |
|-------|-------|-----|
| `xs` | 4px | Icon gap, inline |
| `sm` | 8px | Element gap (default) |
| `md` | 16px | Section gap |
| `lg` | 24px | Card padding |
| `xl` | 32px | Auth card |
| `2xl` | 40px | Page margins (desktop) |
| `3xl` | 48px | Hero padding |
| `4xl` | 64px | TopAppBar height |
| `unit` | 4px | Base unit |
| `container-max` | 1440px | Max content width |

## Utility Classes

```css
/* Padding */
.p-xs  { padding: var(--space-xs); }
.p-sm  { padding: var(--space-sm); }
.p-md  { padding: var(--space-md); }
.p-lg  { padding: var(--space-lg); }
.px-sm { padding-left: var(--space-sm); padding-right: var(--space-sm); }
.px-md { padding-left: var(--space-md); padding-right: var(--space-md); }
.py-sm { padding-top: var(--space-sm); padding-bottom: var(--space-sm); }
.py-md { padding-top: var(--space-md); padding-bottom: var(--space-md); }

/* Gap */
.gap-xs { gap: var(--space-xs); }
.gap-sm { gap: var(--space-sm); }
.gap-md { gap: var(--space-md); }
.gap-lg { gap: var(--space-lg); }

/* Margin */
.mt-xs { margin-top: var(--space-xs); }
.mt-sm { margin-top: var(--space-sm); }
.mt-md { margin-top: var(--space-md); }
.mt-lg { margin-top: var(--space-lg); }
.mb-xs { margin-bottom: var(--space-xs); }
.mb-sm { margin-bottom: var(--space-sm); }
.mb-md { margin-bottom: var(--space-md); }
.mb-lg { margin-bottom: var(--space-lg); }
```
