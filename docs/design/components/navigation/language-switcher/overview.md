# Language Switcher

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Trigger (globe icon + current locale code) + Dropdown (list of available locales)

**States:** Closed · Open (dropdown visible, 4-8 locale options) · Selected (checkmark + active indicator on current locale)

**Locales:** EN (English) · DE (German) · More added via config. Display: locale name in its own language (e.g., "English / EN", "Deutsch / DE").

**Placement:** Top-app-bar (desktop) or settings (mobile). Not visible when only one locale available.

**Persistence:** Cookie (`salus_locale`) set on selection. Page reloads with new locale.

**Do:** Show locale names in native language · Auto-detect from browser initially · Persist selection

**Don't:** Use flag icons for languages (languages ≠ countries) · Auto-redirect if user explicitly selected · Show when only 1 locale

**Accessibility:**
- Trigger: `aria-label="Change language — current: English"`, `aria-expanded`, `aria-haspopup="true"`
- Dropdown: `role="listbox"`, items: `role="option"`, `aria-selected="true/false"`
- Selected locale: `aria-selected="true"`, checkmark icon visible
- Keyboard: Enter/Space opens, Arrow keys navigate, Enter selects and applies

**Related:** `top-app-bar.md`, `nav-dropdown.md`, `icon.md`

**Token Values:**
| Token | Value |
|-------|-------|
| --language-switcher-trigger-font | `var(--font-label-sm)` |
| --language-switcher-trigger-color | `{colors.slate-600}` |
| --language-switcher-item-padding | `8px 12px` |
| --language-switcher-item-font | `var(--font-body-sm)` |
| --language-switcher-item-selected-bg | `{colors.primary-50}` |
| --language-switcher-item-selected-text | `{colors.primary-600}` |
| --language-switcher-checkmark-size | 16px |
