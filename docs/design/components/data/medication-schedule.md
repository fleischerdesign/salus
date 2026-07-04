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
