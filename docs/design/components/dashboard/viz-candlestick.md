# Viz: Candlestick

**Anatomy:** Header (value + unit + delta) + SVG candlestick chart (80px height) + Sub-label

**States:** Default · Up-day (green candle) · Down-day (red candle) · No-data (empty chart with placeholder)

**Sizes:** Medium/Large only. Not available in small.

**Chart:** SVG candlestick bars with high/low wicks and open/close bodies. Green body (tertiary-600) when close > open, red body (error-600) when close < open. Wicks: slate-500. Weekday labels below: Mon-Sun, label-sm.

**Sub-label:** Optional secondary text below chart (label-sm, slate-500).

**Do:** Use for OHLC-based metrics (HRV, blood pressure) · Show weekday labels · Color-code up/down

**Don't:** Use for simple trend (use sparkline) · Omit weekday context · Use without color distinction

**Accessibility:**
- SVG: `role="img"` with `aria-label` describing range (e.g., "HRV this week: ranging from 45 to 72 ms")
- Individual candles not separately interactive
- Colors: green (up) and red (down) supplemented by aria-label pattern

**Related:** `viz-sparkline.md`, `viz-number.md`, `chart-tooltip.md`
