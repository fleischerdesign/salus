# Vital Signs Row

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Compact horizontal row of vital sign cards. Each card: colored icon + value + label + optional trend arrow

**Default signs:**
| Sign | Icon | Color | Unit | Normal Range |
|------|------|-------|------|-------------|
| Heart Rate | `favorite` | metric-heart-rate | bpm | 60–100 |
| Blood Pressure | `monitor_heart` | metric-heart-rate | mmHg | 120/80 |
| SpO2 | `oxygen_saturation` | secondary | % | 95–100 |
| Temperature | `thermostat` | warning-500 | °C | 36.1–37.2 |
| Respiratory Rate | `air` | metric-sleep | /min | 12–20 |

**States:** Normal (no treatment) · Borderline (warning chip) · Abnormal (error chip) · No data ("--")

**Layout:** Flex row, gap: 16px. Each card: flex-1, min-width: 140px. Wrap on mobile.

**Do:** Show all 5 core vitals · Color-code by severity · Show units · Indicate normal range

**Don't:** Omit units · Show without clinical context · Use ambiguous colors

**Accessibility:**
- Each vital card: `role="region"` with `aria-label` describing the vital + value + status
- Status (normal/borderline/abnormal): `aria-label` on the card + color
- Heart rate: additional `aria-live="polite"` if real-time updating

**Token Values:**
| Token | Value |
|-------|-------|
| --vital-card-min-width | 140px |
| --vital-card-gap | 16px |
| --vital-icon-size | 24px |
| --vital-value-font | `var(--font-headline-md)` |
| --vital-label-font | `var(--font-body-sm)` muted |

**Composition:** Flex row of compact cards. Each card: Icon + Value + Unit + Label + optional trend arrow.

**Responsive:** Wraps to 2 columns on tablet, single column on mobile.

**Related:** `stat.md`, `kpi-card.md`, `status-dot.md`, `compare.md`

## Visual Design

### Each Vital Card

| Element | Spec |
|---------|------|
| Icon | 24px, colored per vital type |
| Value | `--font-headline-md` (20px, 600), `--color-on-surface` |
| Unit | `--font-body-sm` (14px), `--color-slate-500`, after value |
| Label | `--font-label-sm` (12px), `--color-slate-500`, below value |
| Trend arrow (optional) | 16px, right of value |

### Status Indicators

| Status | Chip Variant | Dot Color |
|--------|-------------|-----------|
| Normal | Success (tertiary) | `--color-tertiary-500` |
| Borderline | Warning (amber) | `--color-warning-500` |
| Abnormal | Error (red) | `--color-error-500` |
| No data | "--" in `--color-slate-400` | — |

Status chip shown below value (4px gap), `--font-label-sm`.

### Layout
- Flex row, gap 16px
- Each card: flex-1, min-width 140px, padding 12px
- Wrap on mobile

### Spacing
- Card↔Card gap: 16px
- Min card width: 140px
- Icon↔Content gap: 8px

### Responsive
Desktop: all 5 in row. Tablet: 2-3 per row. Mobile: 1 per row, full-width.
