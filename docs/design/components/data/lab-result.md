# Lab Result

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Test name + Value (bold) + Unit + Reference range + Status indicator

**States:** Normal (tertiary/green indicator) · Borderline Low/High (warning/amber) · Abnormal Low/High (error/red) · Critical (error, pulsing or bold-red)

**Reference range:** Shown as muted text: "(Ref: 3.5–5.2)". Status dot or colored background on abnormal values.

**Formatting:** Value: headline-md, bold. Unit: body-sm, muted. Range: body-sm, muted. Status: 8px colored dot left of value.

**Grouping:** Multiple lab results grouped by category (Chemistry, Hematology, etc.) with category header.

**Do:** Show reference range · Color-code abnormal values · Group by category · Show critical values prominently

**Don't:** Show value without range · Use color alone for abnormal · Hide units

**Accessibility:**
- Use `<dl>` (Lab test: `<dt>`, Value+Unit: `<dd>`, Range: `<dd>`)
- Abnormal status: `aria-label` describing severity (e.g., "High — above normal range")
- Color alone insufficient: always include text or aria-label for abnormal values

**Token Values:**
| Token | Value |
|-------|-------|
| --lab-result-value-font | `var(--font-headline-md)` |
| --lab-result-unit-color | `{colors.slate-400}` |
| --lab-result-range-color | `{colors.slate-400}` |
| --lab-result-indicator-size | 8px |

**Related:** `stat.md`, `key-value.md`, `status-dot.md`, `compare.md`

## Visual Design

### Row Layout
- Status dot (8px, left) + Test name (`--font-body-md`) + Value (`--font-headline-md`, bold) + Unit (`--font-body-sm`, `--color-slate-500`) + Reference range (`--font-body-sm`, `--color-slate-400`)

### Status Indicators

| Status | Dot Color | Value Color | Emphasis |
|--------|-----------|------------|----------|
| Normal | `--color-tertiary-500` | `--color-on-surface` | None |
| Borderline Low | `--color-warning-500` | `--color-on-surface` | None |
| Borderline High | `--color-warning-500` | `--color-on-surface` | None |
| Abnormal Low | `--color-error-500` | `--color-error-700` | Value bold |
| Abnormal High | `--color-error-500` | `--color-error-700` | Value bold |
| Critical | `--color-error-500` pulsing | `--color-error-700` bold | Red background tint `--color-error-50`, pulse animation 1.8s |

### Grouping
Category headers: `--font-label-md` (13px, 600), `--color-slate-700`, `1px solid --color-slate-200` border below, padding 8px 0. Gap between groups: 24px.

### Spacing
- Dot↔Name: 8px
- Name↔Value: 4px
- Value↔Unit: 2px
- Unit↔Range: 8px
- Row height: 36px
