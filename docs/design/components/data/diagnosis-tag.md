# Diagnosis Tag

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Chip showing ICD code + Short description

**Variants:**
- Active: primary-100 bg, primary-800 text
- Chronic: chip with chronic icon, warning-100 bg
- Resolved: neutral chip, muted, optionally with check mark
- Primary/Chief complaint: bold border, slightly larger

**Format:** "E11.9 — Type 2 Diabetes" (code + em-dash + name). Code: mono font. Name: sans-serif, body-sm.

**Interaction:** Click/tap for details (tooltip with full description, onset date, status).

**Do:** Show code + name · Distinguish active/chronic/resolved · Support touch for detail

**Don't:** Show code only · Use same style for all statuses · Omit ICD code (clinical requirement)
