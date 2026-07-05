# Confirmation Dialog

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Modal + Icon (warning, 48px) + Title + Description + Primary action button + Cancel button

**States:** Closed · Opening · Open · Confirming (primary button shows loading) · Closed (after confirm)

**Variants:** Danger (error icon + red primary button) · Warning (warning icon + amber button) · Info (info icon + primary button)

**Action:** Primary button executes the destructive/confirming action. Cancel dismisses without action.

**Implementation:** Replaces browser native `confirm()` (hx-confirm fallback). Custom modal with HTMX integration. `hx-confirm` triggers this instead of browser dialog.

**Do:** Use for destructive actions (delete, revoke, disband) · Show icon indicating severity · Provide clear Cancel

**Don't:** Use for non-destructive actions · Omit severity icon · Use generic "Are you sure?" without context

**Accessibility:**
- Inherits all modal accessibility: `role="dialog"`, `aria-modal`, focus trap, Escape close
- Title: `aria-labelledby` referencing heading
- Description: `aria-describedby` explaining consequences
- Danger variant: `aria-live="assertive"` for prominent announcement
- Primary button focused by default, not Cancel (prevents accidental confirm)

**Token Values:**
| Token | Value |
|-------|-------|
| --confirm-icon-size | 48px |
| --confirm-icon-danger | `{colors.error-500}` |
| --confirm-icon-warning | `{colors.warning-500}` |
| --confirm-icon-info | `{colors.primary}` |
| --confirm-content-max-width | 400px |

**Composition:** Modal (Backdrop + Card) containing: Icon + Title + Description + Primary action button + Cancel button.

**Responsive:** Full-width on mobile.

**Related:** `modal.md`, `btn.md`, `icon.md`, `alert.md`

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
