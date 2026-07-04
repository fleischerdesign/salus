# Vital Signs Row

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Compact horizontal row of vital sign cards. Each card: colored icon + value + label + optional trend arrow

**Default signs:**
| Sign | Icon | Color | Unit | Normal Range |
|------|------|-------|------|-------------|
| Heart Rate | `favorite` | metric-heart-rate | bpm | 60–100 |
| Blood Pressure | `monitor_heart` | metric-heart-rate | mmHg | 120/80 |
| SpO2 | `oxygen_saturation` | secondary | % | 95–100 |
| Temperature | `thermostat` | warning-500 | °C | 36.1–37.2 |
| Respiratory Rate | `air` | metric-sleep | /min | 12–20 |

**States:** Normal (no treatment) · Borderline (warning chip) · Abnormal (error chip) · No data ("--")

**Layout:** Flex row, gap: 16px. Each card: flex-1, min-width: 140px. Wrap on mobile.

**Do:** Show all 5 core vitals · Color-code by severity · Show units · Indicate normal range

**Don't:** Omit units · Show without clinical context · Use ambiguous colors
