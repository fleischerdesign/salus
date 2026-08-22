# Specification: Modern Theme System (Phase 5 - Tailwind v4 OkLCH & Reactive Settings)

## 1. Problem Statement

The theme system in Salus was partially decoupled during the Tailwind v4 and Glassmorphism redesign:

1. `SettingsPage.svelte` (Appearance tab) maintains detached local `$state` variables and does not read from or write to the central `theme` store (`$lib/stores/theme.svelte.ts`).
2. The interactive `HueRing.svelte` and `ACCENT_HUES` preset chips are not exposed in the UI.
3. CSS variables in `frontend/src/app.css` use fixed hex values for `--color-primary` and `--color-primary-soft`, ignoring the user's `--accent-hue`.
4. Surface tokens in the `@theme` block of `app.css` contain circular references (`--color-surface-300: var(--color-surface-300)`).

## 2. User Stories

- **As a user**, I want changes in the Appearance settings (Light, Dark, System mode, Colorblind toggle, Accent Hue) to immediately take effect across the entire application and persist across sessions and devices.
- **As a user**, I want to pick my preferred accent color via preset chips or an interactive color ring while retaining WCAG 2.2 AA compliant contrast on glass and card surfaces.
- **As a user with color vision deficiency**, I want colorblind mode in settings to reliably adapt semantic status indicators (shifting green success to distinguishable blue).

## 3. Acceptance Criteria (Gherkin)

```gherkin
Feature: Reactive Theme & Accent Controller

  Scenario: Switching theme mode in Settings
    Given the user navigates to "/settings/app" (Appearance tab)
    When the user clicks "Hell", "Dunkel", or "System"
    Then the application's "data-theme" attribute updates immediately on document element
    And the active theme mode button is visibly highlighted
    And the preference is persisted to localStorage and synchronized to the user profile

  Scenario: Toggling colorblind mode in Settings
    Given the user navigates to "/settings/app"
    When the user toggles colorblind mode on
    Then the "data-colorblind" attribute is set to "true" on document element
    And semantic success indicators shift to the colorblind-safe blue palette
    And the preference is persisted and synchronized

  Scenario: Customizing accent hue via preset chips
    Given the user is on the Appearance settings tab
    When the user clicks an accent preset chip (e.g., Emerald, Ocean, Rose, Amber)
    Then "--accent-hue" updates dynamically on the document root
    And all primary-accented elements (buttons, active navigation pills, focus rings) update their hue
    And the active chip shows a selected indicator

  Scenario: Customizing accent hue via interactive HueRing
    Given the user drags or clicks the HueRing component
    When the hue changes to a custom degree (0-360)
    Then the theme's accent hue updates reactively
    And the primary color ramp adapts smoothly using OkLCH color space

  Scenario: Tailwind v4 surface tokens resolution
    Given the application renders in light or dark mode
    Then all surface color classes (surface-0 through surface-900) map cleanly to their corresponding background variables without circular self-references
```

## 4. Technical Architecture & Constraints

- **Primary Color Math**:
  - Light mode: `--color-primary: oklch(0.55 0.22 var(--accent-hue))`, `--color-primary-soft: oklch(0.95 0.04 var(--accent-hue) / 0.8)`
  - Dark mode: `--color-primary: oklch(0.70 0.19 var(--accent-hue))`, `--color-primary-soft: oklch(0.30 0.08 var(--accent-hue) / 0.35)`
  - Fallbacks: default `--accent-hue: 250` (or 290) defined on `:root`
- **Domain Colors**:
  - Category/domain colors (`vital`, `activity`, `hydrate`, `fasting`, `circadian`, `sleep`, `success`) remain fixed domain pillars and do not mutate with accent hue.
- **Store & Settings**:
  - `SettingsPage.svelte` binds to `theme.mode`, `theme.colorblind`, and `theme.accentHue`
  - Optimistic local update with debounced profile synchronization.

## 5. Out of Scope

- Arbitrary free-form text editing of arbitrary CSS tokens.
- Custom fonts beyond Manrope / JetBrains Mono.
