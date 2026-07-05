# Stat / Metric Display

**Anatomy:** Large numeric value + Unit + Optional label + Optional trend delta

**States:** Default · Positive trend (success ↑) · Negative trend (error ↓) · Neutral (muted →) · No-data ("--" placeholder, never blank or "0")

**Sizes:** Compact (32px number, sidebar) · Standard (36px number, dashboard widgets) · Hero (48px number, KPI cards)

**Formatting:** Steps: comma-separated integer. Weight: 1 decimal + "kg". Heart rate: integer + "bpm". Sleep: "Xh Ym". Duration: "Xh Ym". Percentage: "XX%".

**Trend delta:** Arrow icon + percentage/text. Positive (success): ↑. Negative (error): ↓. Neutral (muted): →.

**Fallback:** "--" when no data. Not blank, not "0".

**Do:** Use large bold numbers · Show unit · Add trend direction · Show "--" for missing data

**Don't:** Use for multi-value display (use key-value list) · Omit unit · Show "0" when data is missing

**Accessibility:**
- Main value: `aria-label` describing what it represents (e.g., "Heart rate: 72 beats per minute")
- Trend delta: `aria-label` describing direction + magnitude (e.g., "Increased by 5% from yesterday")
- Fallback: "--" for missing data, never empty or "0"

**Related:** `key-value.md`, `anim-number.md`, `compare.md`, `progress-bar.md`

## Visual Design

### Sizes & Typography

| Size | Number Font | Number Size | Unit Size | Context |
|------|------------|-------------|-----------|---------|
| Compact | `--font-headline-md` (20px, 600) | 20px | `--font-body-sm` (14px) | Sidebar |
| Standard | `--font-headline-lg` (28px, 700) | 28px | `--font-body-md` (16px) | Dashboard widgets |
| Hero | `--font-display` (48px, 800) | 48px | `--font-headline-md` (20px) | KPI cards |

### Anatomy
- Label: `--font-label-sm`, `--color-slate-500`, above number, 4px gap
- Number: large, bold, `--color-on-surface`
- Unit: `--color-slate-500`, after number, 4px gap
- Delta: arrow icon + text, below or right of unit, 4px gap

### Delta / Trend

| Direction | Icon | Color | Meaning |
|-----------|------|-------|---------|
| Positive | ↑ | `--color-tertiary-600` | Good (increase is desired) |
| Negative | ↓ | `--color-error-600` | Bad (decrease is desired) |
| Neutral | → | `--color-slate-500` | No significant change |

Delta font: `--font-label-sm` (12px, 600).

### States
| State | Number | Delta |
|-------|--------|-------|
| Default | Value + unit | ± arrow if available |
| Loading | Skeleton 24px × 80px | Hidden |
| No data | "--" (em dash), `--color-slate-400` | Hidden |

### Formatting
- Steps: `12,345` (comma-separated integer)
- Weight: `72.5 kg` (1 decimal)
- Heart rate: `72 bpm` (integer)
- Sleep: `7h 32m` (hours + minutes)
- Duration: `1h 15m`
- Percentage: `78%`

### Spacing
- Label↔Number: 4px
- Number↔Unit: 4px
- Number↔Delta: 8px (right) or 4px (below)
