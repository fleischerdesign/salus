## Visual Design

### Colors & Meanings

| Color Token | Color | Meaning | Animation |
|------------|-------|---------|-----------|
| `--color-tertiary-500` | Emerald | Active / Online / Healthy / Normal | None |
| `--color-warning-500` | Amber | Pending / Warning / Degraded | None |
| `--color-error-500` | Red | Inactive / Offline / Error / Critical | None |
| `--color-slate-400` | Slate | Unknown / No data / Neutral | None |
| `--color-primary-500` | Indigo | Syncing / Processing | Pulsing 1.8s |

### Sizes
| Variant | Diameter | Use |
|---------|----------|-----|
| Standard | 8px | Next to labels, table cells |
| Small | 6px | Inline with text |

### Animation
- Syncing/Processing: opacity pulse 0.4→1.0→0.4, 1.8s ease-in-out infinite
- All other states: static
- `prefers-reduced-motion`: static (no pulse), all states

### Placement
- Next to text: inline, 4px gap, vertically centered with text baseline
- On avatar: absolute position, bottom-right, 2px white border ring
- In table: left of text in cell

### Spacing
- Dot↔Label: 4px
- On avatar: bottom 0, right 0, 2px white ring
