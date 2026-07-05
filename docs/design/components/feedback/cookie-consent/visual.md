## Visual Design

### Appearance
- **Background:** `--color-slate-900`
- **Text:** `--color-slate-50`, `--font-body-sm`
- **Padding:** 24px
- **Top radius:** `--radius-xl` (16px top, 0 bottom — bottom-attached banner)
- **Icon:** 24px cookie icon, `--color-slate-300`, left
- **Z-index:** `--z-tooltip` (500)
- **Shadow:** `--shadow-xl` (above banner)

### Anatomy
- Fixed bottom of viewport, full-width
- Row: Icon (24px) + Description text (flex-1) + Buttons (Accept All primary + Settings link)
- Gap: 16px between elements

### States
| State | Visual |
|-------|--------|
| Visible | Slide-up from bottom, 300ms ease-out |
| Dismissing | Slide-down + fade, 200ms ease-in |
| Settings open | Modal overlay (see `modal.md`) with category toggles |

### Settings Modal
- Categories: Essential (always on, disabled toggle), Analytics (default off), Preferences (default off)
- Per-category: Toggle + Label + Description
- Buttons: "Save Settings" (primary) + "Accept All" (ghost)

### Spacing
- Horizontal padding: 24px
- Vertical padding: 24px
- Icon↔Text: 16px
- Text↔Buttons: 16px
- Button↔Button gap: 8px

### Responsive
`< --bp-mobile`: Buttons stack below text. Icon hidden or smaller (20px). Padding: 16px.
