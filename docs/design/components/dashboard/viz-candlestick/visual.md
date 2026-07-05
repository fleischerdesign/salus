## Visual Design

### Appearance
- **Chart:** SVG, 80px height, full widget width
- **Candle body:** 6px width. Green (`--color-tertiary-600`) when close > open. Red (`--color-error-600`) when close < open
- **Wicks:** 1px `--color-slate-500`, vertical from high to low, 1px width
- **Labels:** weekday abbreviations (Mon-Sun), `--font-label-sm` (10px), `--color-slate-400`, below each candle
- **Header:** value + unit + delta, above chart

### States
| State | Visual |
|-------|--------|
| Default | Green/red candles per day |
| Up day (close > open) | Green body |
| Down day (close < open) | Red body |
| Weekend | Lighter opacity (0.6) |
| No data | Empty chart, "--" placeholder |

### Colors
- Up (green): `--color-tertiary-600`
- Down (red): `--color-error-600`
- Wicks: `--color-slate-500`
- Weekend: opacity 0.6

### Sizes
Medium+ widgets only. Not for small.
