## Visual Design

### Appearance
- **Target:** monospace text (`--font-code-sm`), `--color-slate-100` bg, padding 8px 12px, `--radius-sm`, `1px solid --color-slate-200`
- **Copy button:** 28×28px ghost icon-only button, `content_copy` icon 16px, right of target, gap 8px
- **Success state:** icon → `check` (16px, `--color-tertiary-600`), tooltip "Copied!"
- **Error state:** icon → `error` (16px, `--color-error-600`), tooltip "Failed to copy"

### States
| State | Icon | Color | Duration |
|-------|------|-------|----------|
| Default | `content_copy` | `--color-slate-500` | — |
| Hover | `content_copy` | `--color-slate-700` | — |
| Copied | `check` | `--color-tertiary-600` | 2s, then reverts |
| Error | `error` | `--color-error-600` | Until dismissed |

Transition: 150ms ease-default icon switch.

### Spacing
- Target↔Button gap: 8px
- Target padding: 8px 12px
- Button: 28×28px, icon: 16px
