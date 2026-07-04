# Diagnosis Tag

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Chip showing ICD code + Short description

**States:** Active (primary-100 bg) · Chronic (warning-100 bg, chronic icon) · Resolved (neutral chip, muted, optional check mark) · Primary/Chief complaint (bold border, slightly larger)

**Variants:**
- Active: primary-100 bg, primary-800 text
- Chronic: chip with chronic icon, warning-100 bg
- Resolved: neutral chip, muted, optionally with check mark
- Primary/Chief complaint: bold border, slightly larger

**Format:** "E11.9 — Type 2 Diabetes" (code + em-dash + name). Code: mono font. Name: sans-serif, body-sm.

**Interaction:** Click/tap for details (tooltip with full description, onset date, status).

**Do:** Show code + name · Distinguish active/chronic/resolved · Support touch for detail

**Don't:** Show code only · Use same style for all statuses · Omit ICD code (clinical requirement)

**Accessibility:**
- `aria-label` with full diagnosis: "E11.9 — Type 2 Diabetes, Active"
- Code: `<code>` element for machine-readable clinical code
- Tooltip: `aria-describedby` linking to detail panel
- Chip status: distinct colors + text labels (not color alone)

**Token Values:**
| Token | Value |
|-------|-------|
| --diagnosis-code-font | `var(--font-family-mono)` 13px |
| --diagnosis-name-font | `var(--font-body-sm)` |
| --diagnosis-active-bg | `{colors.primary-100}` |
| --diagnosis-chronic-bg | `{colors.warning-100}` |
| --diagnosis-resolved-bg | `{colors.slate-100}` |

**Related:** `chip.md`, `chip-row.md`, `tooltip.md`
