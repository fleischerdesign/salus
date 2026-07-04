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
