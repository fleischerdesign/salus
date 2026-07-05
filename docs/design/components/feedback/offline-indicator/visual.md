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
