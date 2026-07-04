# Status Dot

**Anatomy:** 8px colored circle indicating current state. Distinct from Badge (which shows a count).

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
