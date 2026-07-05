# Cookie Consent Banner

> Status: **Design spec only — not yet implemented.** GDPR/DSGVO compliance required.

**Anatomy:** Fixed bottom banner with: Cookie icon + Description text + "Accept All" button + "Settings" link

**States:** Visible (first visit) · Dismissed (after accept or settings saved) · Settings open (modal with per-category toggles)

**Categories:** Essential (always on, disabled toggle). Analytics (optional). Preferences (optional — theme, locale).

**Appearance:** Slate-900 bg (dark), slate-50 text. 16px horizontal padding, 24px vertical. Rounded-xl top corners. z-tooltip (500).

**Animation:** Slide-up from bottom (300ms ease-out). Dismiss: slide-down + fade (200ms ease-in).

**Persistence:** Cookie (`salus_cookie_consent`) stores preferences. Never shown again after explicit choice.

**Do:** Show on first visit · Block non-essential cookies until consent · Provide granular settings · Log consent timestamp

**Don't:** Auto-dismiss without choice · Set non-essential cookies before consent · Obscure page content completely

**Accessibility:**
- Banner: `role="dialog"` with `aria-label="Cookie consent"`
- Focus moved to banner on appearance
- Settings: toggles per category with `role="switch"` + `aria-checked`
- Dismiss on explicit choice only (Accept All or Save Settings)

**Token Values:**
| Token | Value |
|-------|-------|
| --cookie-banner-bg | `{colors.slate-900}` |
| --cookie-banner-text | `{colors.slate-50}` |
| --cookie-banner-padding | `24px` |
| --cookie-banner-radius | `var(--radius-xl)` |
| --cookie-banner-z-index | `var(--z-tooltip)` |
| --cookie-banner-animation-in | slide-up 300ms ease-out |
| --cookie-banner-animation-out | slide-down+fade 200ms ease-in |

**Composition:** Cookie icon + Description text + Accept All button + Settings link. Fixed at bottom of viewport.

**Related:** `btn.md`, `icon.md`, `toggle.md`, `modal.md`
