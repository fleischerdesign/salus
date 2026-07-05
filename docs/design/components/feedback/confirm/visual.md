## Visual Design

### Variants

| Variant | Icon | Icon Color | Primary Button Variant | Use |
|---------|------|-----------|----------------------|-----|
| Danger | warning 48px | `--color-error-500` | Danger (`btn-danger`) | Delete, revoke, disband |
| Warning | warning 48px | `--color-warning-500` | Secondary + amber text | Discard changes, leave group |
| Info | info 48px | `--color-primary` | Primary | Publish, share, send |

### Anatomy
- Modal (see `modal.md`): Backdrop + Content panel, max-width 400px
- Content: Icon (48px, centered) → Title (`--font-headline-md`, centered) → Description (`--font-body-sm`, centered, `--color-slate-600`) → Buttons (row, gap 8px, right-aligned or centered)

### States
| State | Primary Button | Cancel Button |
|-------|---------------|---------------|
| Default | Active, variant per type | Ghost, "Cancel" |
| Hover | Variant hover | Ghost hover (slate-100) |
| Confirming (loading) | Disabled, spinner replaces text | Disabled |
| Complete | Modal closes, follow-up feedback (toast/redirect) | — |

### Spacing
- Icon↔Title: 16px
- Title↔Description: 8px
- Description↔Buttons: 24px
- Button↔Button gap: 8px

### Focus
Default focus: Cancel button (not primary — prevents accidental destructive action). Escape: dismisses. Enter: activates focused button.
