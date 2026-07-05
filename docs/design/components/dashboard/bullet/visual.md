## Visual Design

### Appearance
- **Bar height:** 24px
- **Background bands:** sequential slate shades (slate-100, slate-200, slate-300), each proportional to their range
- **Performance bar:** `--color-primary-600`, shorter than full width, sits on top of bands
- **Target marker:** `2px solid --color-slate-900` vertical line at target position

### States
| State | Performance Bar | Target Marker |
|-------|----------------|---------------|
| Below target | `--color-primary-600` | Right of performance bar |
| At target | `--color-primary-600` | Aligned with bar end |
| Above target | `--color-tertiary-600` | Left of performance bar |
| No data | "--" placeholder, empty bar | — |

### Colors
- Poor band: `--color-slate-100`
- Satisfactory band: `--color-slate-200`
- Good band: `--color-slate-300`
- Performance: `--color-primary-600`
- Target: `2px --color-slate-900`

### Spacing
- Bar height: 24px
- Target marker: 2px wide, full bar height
- Bands: stacked within bar, 0 gap
