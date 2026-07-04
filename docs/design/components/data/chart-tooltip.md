# Chart Tooltip

**Tokens:** `--chart-tooltip-bg`, `--chart-tooltip-text`, `--chart-tooltip-border`

**Anatomy:** Floating box with data point details

**Appearance:** Slate-800 bg, slate-50 text, label-sm font, 8px padding, 6px radius, subtle border. Appears on hover near data point.

**States:** Hidden (opacity 0, transform scale 0.95) · Visible (opacity 1, scale 1, 150ms transition)

**Position:** Follows mouse with 12px offset. Constrained within chart container.

**Contents:** Date + Value (bold) + optional unit or context.

**Do:** Show on chart hover · Constrain within chart bounds · Show relevant data point info

**Don't:** Obscure data point · Overflow chart container · Show redundant info

**Accessibility:**
- Tooltip content associated via `aria-describedby` on chart data point
- Data points: `role="img"` with `aria-label` describing the value
- Mouse users see visual tooltip; keyboard users access equivalent info via aria-label
- Tooltip itself: `role="tooltip"` (informational, non-interactive)

**Token Values:**
| Token | Value |
|-------|-------|
| --tooltip-bg | `{colors.slate-800}` |
| --tooltip-text | `{colors.slate-50}` |
| --tooltip-border | `1px solid rgba(255,255,255,0.15)` |
| --tooltip-radius | `6px` |
| --tooltip-padding | `8px` |
| --tooltip-font | `var(--font-label-sm)` |
| --tooltip-offset | `12px` |

**Related:** `tooltip.md` (feedback/tooltip), `viz-*.md`
