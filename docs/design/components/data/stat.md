# Stat / Metric Display

**Anatomy:** Large numeric value + Unit + Optional label + Optional trend delta

**Sizes:** Compact (32px number, sidebar) · Standard (36px number, dashboard widgets) · Hero (48px number, KPI cards)

**Formatting:** Steps: comma-separated integer. Weight: 1 decimal + "kg". Heart rate: integer + "bpm". Sleep: "Xh Ym". Duration: "Xh Ym". Percentage: "XX%".

**Trend delta:** Arrow icon + percentage/text. Positive (success): ↑. Negative (error): ↓. Neutral (muted): →.

**Fallback:** "--" when no data. Not blank, not "0".

**Do:** Use large bold numbers · Show unit · Add trend direction · Show "--" for missing data

**Don't:** Use for multi-value display (use key-value list) · Omit unit · Show "0" when data is missing
