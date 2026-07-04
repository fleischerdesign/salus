# Language Switcher

**Anatomy:** Radio group or select dropdown showing available languages

**States:** Selected (current locale) · Unselected

**Display format:** "English (EN)" or "Deutsch (DE)". Label in both native and current language.

**Implementation:** `hx-post` to locale endpoint. Sets `salus_locale` cookie. Page refreshes with translation updates.

**Options:** EN (English) · DE (Deutsch). Extensible to more languages via i18n system.

**Do:** Show native language name · Apply immediately · Persist in cookie · Use radio group for ≤5 languages

**Don't:** Require page reload (HTMX partial update preferred) · Use flags for languages (political) · Show unavailable languages
