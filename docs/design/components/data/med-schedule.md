# Medication Schedule

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Time-based list of medication entries. Each: time + drug name + dosage + status chip

**States:**
- Upcoming: neutral chip, muted text
- Due now: warning chip, subtle highlight bg
- Taken: success chip + checkmark + timestamp
- Missed: error chip + alert icon
- Skipped (intentional): neutral chip, strikethrough

**Dosage format:** "500mg" · "1 Tablet" · "2 puffs" · "10ml". Bold weight.

**Time display:** "08:00" or relative: "in 30 min", "2h ago". Upcoming items show countdown on hover.

**Adherence ring:** Optional mini progress ring showing daily adherence % next to schedule title.

**Do:** Show clear status per dose · Indicate upcoming/due/missed · Use chip colors consistently · Show dosage clearly

**Don't:** Omit time context · Use ambiguous status labels · Forget adherence summary

**Responsive:** Single-column dose list. Adherence ring shrinks on mobile. Time display stays inline with medication name.

**Accessibility:**
- Use `<ol>` with `<li>` for chronological schedule
- Each dose: `<time>` for scheduled time, `<span>` or chip for status
- Status chips: `aria-label` describing state (e.g., "Taken at 08:15")
- Adherence ring: `role="progressbar"` with day completion value

**Token Values:**
| Token | Value |
|-------|-------|
| --med-schedule-time-font | `var(--font-body-md)` bold |
| --med-schedule-dosage-font | `var(--font-body-md)` |
| --med-schedule-adherence-ring-size | 48px |
| --med-schedule-due-highlight | `{colors.warning-50}` |
| --med-schedule-missed-color | `{colors.error-500}` |

**Related:** `chip.md`, `progress-bar.md`, `list-item.md`, `timeline.md`

## Visual Design

### Row Layout
- Time (`--font-body-md`, bold, 60px width) + Drug name (`--font-body-md`) + Dosage (`--font-body-md`, bold) + Status chip (right)

### Status Chips

| Status | Chip Variant | Icon | Highlight |
|--------|------------|------|-----------|
| Upcoming | Neutral | none | none |
| Due now | Warning | `schedule` 16px | `--color-warning-50` bg row |
| Taken | Success | ✓ 14px | none |
| Missed | Error | `warning` 14px | none |
| Skipped | Neutral, strikethrough | none | none |

### Adherence Ring
- 48px SVG ring, 6px stroke, `--color-slate-100` track
- Fill: `--color-tertiary` proportional to adherence %
- Center: percentage text, `--font-label-sm` (12px, 700)
- Position: right of schedule title

### Time Display
- Absolute: "08:00", `--font-body-md`, bold
- Relative (hover): "in 30 min", `--font-caption`, `--color-slate-500`

### Spacing
- Row height: 40px, padding 8px 0
- Time column: 60px
- Row gap: 2px (`1px --color-slate-100` divider between rows)
