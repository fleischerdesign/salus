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
