# Federation Status Indicator

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Status dot (colored) + Label ("Synced 2m ago" / "Sync failed" / "Not synced yet") + Optional retry button

**States:** Synced recently (tertiary dot, "Synced Xm ago") · Syncing (primary dot, pulsing) · Sync failed (error dot, "Sync failed — Retry") · Never synced (slate-400 dot, "Not synced yet")

**Placement:** Below peer handle in peer-card, only visible for remote peers. Compact, 11px caption font.

**Dot:** 8px circle, rounded-full. Pulsing animation (1.8s) when syncing.

**Retry:** Small ghost button, appears only on failed state.

**Do:** Show for all remote peers · Distinguish syncing/synced/failed · Provide retry on failure

**Don't:** Show for local peers · Use ambiguous labels · Omit timestamp on last success

**Accessibility:**
- Status: `aria-label` describing sync state (e.g., "Last synced 2 minutes ago", "Sync failed — click to retry")
- Dot: `aria-hidden="true"` (status communicated in text/aria-label)
- Pulsing (syncing): respects `prefers-reduced-motion`
- Retry button: `aria-label="Retry federation sync"`
- Never synced: `aria-label="Not synced yet"`

**Token Values:**
| Token | Value |
|-------|-------|
| --federation-dot-size | 8px |
| --federation-font | `var(--font-caption)` |

**Related:** `status-dot.md`, `peer-card.md`, `btn.md`, `icon.md`

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
