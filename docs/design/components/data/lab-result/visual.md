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
