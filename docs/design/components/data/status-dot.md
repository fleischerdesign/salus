# Status Dot

**Anatomy:** 8px colored circle indicating current state. Distinct from Badge (which shows a count).

**States:** Active/Online (tertiary-500) · Pending/Warning (warning-500) · Error/Offline (error-500) · Unknown/Neutral (slate-400) · Syncing/Processing (primary-500, pulsing)

**Variants:**
| Color | Meaning |
|-------|---------|
| tertiary-500 | Active / Online / Normal / Healthy |
| warning-500 | Pending / Warning / Degraded / Attention needed |
| error-500 | Inactive / Offline / Error / Critical / Abnormal |
| slate-400 | Unknown / No data / Neutral / Disabled |
| primary-500 | Syncing / Processing / In progress |

**Animation:** Pulsing (1.8s opacity cycle) for "in progress" / "syncing" states.

**Placement:** Next to label text, 4px gap. Or absolutely positioned on avatar (see `avatar.md`).

**Do:** Use for live status indication · Color-code consistently · Add pulsing for transient states · Use next to labels

**Don't:** Use for counts (use Badge) · Rely on color alone (also show text label) · Change colors without context

**Accessibility:**
- `aria-label` describing status (e.g., "Online", "Syncing", "Error")
- If placed on avatar: `aria-label` on avatar includes status
- Color alone is not sufficient — always accompanied by text or aria-label
- Pulsing animation respects `prefers-reduced-motion`: static instead of pulsing

**Token Values:**
| Token | Value |
|-------|-------|
| --status-dot-size | 8px |
| --status-active-color | `{colors.tertiary-500}` |
| --status-pending-color | `{colors.warning-500}` |
| --status-error-color | `{colors.error-500}` |
| --status-unknown-color | `{colors.slate-400}` |
| --status-syncing-color | `{colors.primary-500}` |
| --status-pulse-duration | 1.8s |

**Related:** `badge.md`, `chip.md`, `avatar.md`, `federation-status.md`
