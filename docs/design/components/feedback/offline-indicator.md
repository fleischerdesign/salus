# Offline Indicator

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Fixed top banner below TopAppBar. Icon (cloud_off) + "You are offline. Changes will sync when connection is restored."

**States:** Hidden (online) · Visible (offline) · Reconnecting (spinner + "Reconnecting...") · Restored (success toast, banner hides after 2s)

**Detection:** `navigator.onLine` + `online`/`offline` window events. No polling needed.

**Appearance:** Warning-100 bg, warning-800 text, body-sm font, 12px padding, full-width. z-sticky (200).

**Do:** Detect via browser events · Show at top of viewport · Auto-hide on reconnect · Queue changes locally

**Don't:** Poll for connectivity · Block interactions · Show error color (offline ≠ error)
