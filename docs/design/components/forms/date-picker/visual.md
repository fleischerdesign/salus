## Visual Design

### Appearance
- **Input:** matches standard Input (44px), 200px width
- **Calendar icon:** 20px, `--color-slate-400`, right side 12px
- **Calendar panel:** `#ffffff` bg, `--shadow-lg`, `--radius-md`, 280px width, `--z-dropdown`
- **Header:** `--font-label-md`, month/year centered, prev/next arrow buttons (28×28px ghost)
- **Day grid:** 7 columns (Su-Sa), `--font-label-sm` headers, `--color-slate-400` headers
- **Day cell:** 36×36px, `--font-body-sm`, rounded-sm

### States

| Element | Default | Hover | Selected | Today | Disabled |
|---------|---------|-------|----------|-------|----------|
| Day cell | transparent | `--color-slate-100` | `--color-primary` bg, white text | `2px solid --color-primary` border | `--color-slate-300` text |
| Input trigger | slate-300 border | slate-400 border | — | — | opacity 0.5 |

### Calendar navigation
- Month/year header: prev/next chevron buttons (20px). Click changes month.
- Today button below grid: ghost button, `--font-label-sm`, jumps to today's date.

### Spacing
- Cell size: 36×36px, 2px gap
- Panel padding: 12px
- Header↔Grid gap: 8px

### Responsive
Desktop: calendar panel attached to input. Mobile: use native `<input type="date">`.
