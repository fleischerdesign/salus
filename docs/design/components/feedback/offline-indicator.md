# Offline Indicator

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Fixed top banner below TopAppBar. Icon (cloud_off) + "You are offline. Changes will sync when connection is restored."

**States:** Hidden (online) · Visible (offline) · Reconnecting (spinner + "Reconnecting...") · Restored (success toast, banner hides after 2s)

**Detection:** `navigator.onLine` + `online`/`offline` window events. No polling needed.

**Appearance:** Warning-100 bg, warning-800 text, body-sm font, 12px padding, full-width. z-sticky (200).

**Do:** Detect via browser events · Show at top of viewport · Auto-hide on reconnect · Queue changes locally

**Don't:** Poll for connectivity · Block interactions · Show error color (offline ≠ error)

**Accessibility:**
- `role="alert"` when connection status changes (important announcement)
- `aria-live="assertive"` for "You are offline" on disconnect
- `aria-live="polite"` for "Back online" on reconnect
- Auto-dismiss on reconnect: `aria-label` still announces restoration

**Token Values:**
| Token | Value |
|-------|-------|
| --offline-banner-bg | `{colors.warning-100}` |
| --offline-banner-text | `{colors.warning-800}` |
| --offline-banner-padding | `12px` |
| --offline-banner-z-index | `var(--z-sticky)` |
| --offline-reconnect-color | `{colors.tertiary-500}` |

**Related:** `toast.md`, `alert.md`, `status-dot.md`

## Visual Design

### Appearance
- **Background:** `--color-warning-100`
- **Text:** `--color-warning-800`, `--font-body-sm`
- **Padding:** 12px
- **Full-width:** below top-app-bar
- **Icon:** 20px, `--color-warning-600` (cloud_off), left of message
- **Z-index:** `--z-sticky` (200)
- **Shadow:** `--shadow-sm` (subtle separation from header)

### Anatomy
- Fixed top, full-width, below header
- Row: Icon (20px) + Message (flex-1) + Optional action button
- Animation: slide-down from behind header, 200ms ease-out

### States

| State | Icon | Message | Color |
|-------|------|---------|-------|
| Hidden | — | — | Not rendered |
| Offline | cloud_off (20px, warning-600) | "You are offline. Changes will sync when connection is restored." | Warning-100 bg |
| Reconnecting | sync (20px, primary), spinning | "Reconnecting..." | `--color-primary-100` bg, `--color-primary-800` text |
| Restored | check_circle (20px, tertiary-600) | "Back online" → auto-hide after 2s | Success flash (tertiary-50 bg, tertiary-800 text) |

### Detection
Browser: `navigator.onLine` + `online`/`offline` events. No polling.

### Spacing
- Padding: 12px horizontal, 10px vertical
- Icon↔Message: 8px

### Responsive
Full-width. Text wraps on mobile. No responsive overrides needed.
