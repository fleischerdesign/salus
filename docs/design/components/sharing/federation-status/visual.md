## Visual Design

### States

| Status | Dot Color | Dot Animation | Label | Retry |
|--------|-----------|-------------|-------|-------|
| Synced recently | `--color-tertiary-500` | None | "Synced 2m ago" | Hidden |
| Syncing | `--color-primary-500` | Pulse 1.8s | "Syncing..." | Hidden |
| Sync failed | `--color-error-500` | None | "Sync failed" | Ghost btn, "Retry" |
| Never synced | `--color-slate-400` | None | "Not synced yet" | Hidden |

### Anatomy
Status dot (8px, left) + Label (`--font-caption`, 11px) + Retry button (right, only on failed)

### Spacing
- Dot↔Label: 4px
- Label↔Retry: 8px
- Placement: below peer handle in peer-card

### Placement
Only visible for remote peers. Below handle name in peer-card. Compact, 11px caption.
