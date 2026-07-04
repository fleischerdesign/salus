# Allergy Badge

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Icon (error-red) + Allergen name + Severity indicator

**Severity levels:**
- Mild: warning-500 dot, body-sm text
- Moderate: warning-700 dot, semi-bold text
- Severe: error-600 dot, bold text + alert icon
- Anaphylaxis: error-700 bg + white text + warning icon — always displayed prominently

**Placement:** Patient header, always visible. Never hidden behind scroll or collapsed section.

**List:** Multiple allergies shown as chip row. Severe/anaphylaxis always first in list.

**Do:** Show prominently · Sort by severity · Use error/warning colors · Always visible in patient context

**Don't:** Hide behind accordion · Omit severity · Use neutral colors for any allergy

**Accessibility:**
- `aria-label` describing allergen + severity (e.g., "Penicillin — Severe allergy")
- Severe/Anaphylaxis: `role="alert"` for priority announcement
- List: `<ul>` with each allergy as `<li>`
- Color + icon: supplemented by aria-label (not color alone)

**Token Values:**
| Token | Value |
|-------|-------|
| --allergy-icon-size | 20px |
| --allergy-mild-color | `{colors.warning-500}` |
| --allergy-moderate-color | `{colors.warning-700}` |
| --allergy-severe-color | `{colors.error-600}` |
| --allergy-anaphylaxis-bg | `{colors.error-700}` |
| --allergy-anaphylaxis-text | `#ffffff` |

**Related:** `chip.md`, `status-dot.md`, `chip-row.md`
