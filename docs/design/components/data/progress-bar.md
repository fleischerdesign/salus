# Progress Bar

**Anatomy:** Track (slate-100, rounded-full, 8px height) + Fill (color varies, rounded-full, animated width)

**Color variants by context:**

| Context | Fill Color |
|---------|-----------|
| Default / Pending | `{colors.primary}` |
| Success / Fulfilled | `{colors.tertiary}` |
| Danger / Missed | `{colors.metric-heart-rate}` |

**States:** Empty (0%) · Partial · Complete (100%) · Indeterminate (animated stripe, for unknown duration)

**Animation:** Width transition 300-500ms ease-default.

**Overlay text:** Percentage centered inside fill (only when bar height ≥16px). Font: label-sm, bold, responsively colored.

**Do:** Use for quantitative progress · Animate width changes · Show percentage when bar is tall enough

**Don't:** Use for non-progress indicators · Animate too fast (>300ms) · Omit accessible label
