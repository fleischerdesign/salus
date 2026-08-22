# Specification: True Neutral Dark Mode (Zero Blue Tint)

## 1. Problem Statement

The dark mode tokens in `frontend/src/app.css` currently use Tailwind's Slate palette (hues 210°–222°), which introduces a noticeable cool blue/navy undertone across all dark canvases, cards, text, and glass dock backgrounds. This creates unwanted color bleeding against warm or neutral accent colors and distracts from clinical and vital domain indicators.

## 2. User Stories

- **As a user**, I want a calm, true neutral dark mode based on a pure grayscale/zinc palette so that the application interface looks modern, clean, and avoids unwanted blue tinting.
- **As a user**, I want text, borders, and glass surfaces to remain sharp, highly readable, and WCAG AA compliant on true dark backgrounds.

## 3. Acceptance Criteria (Gherkin)

```gherkin
Feature: True Neutral Dark Mode

  Scenario: Dark mode background surfaces use pure neutral scale
    Given the application is rendered with data-theme="dark" (or html.dark)
    Then "--bg-canvas" is "#09090b"
    And "--bg-surface-0" is "#121214"
    And "--bg-surface-50" is "#18181b"
    And "--bg-surface-100" is "#232326"
    And "--bg-surface-200" is "#2e2e33"
    And "--color-surface-300" through "--color-surface-900" use neutral zinc/monochrome shades

  Scenario: Dark mode typography and glass tokens use neutral tones
    Given the application is rendered in dark mode
    Then "--text-main" is "#fafafa" (near-pure white, >= 12:1 contrast against surface-0)
    And "--text-muted" is "#a1a1aa" (neutral mid-gray, >= 4.5:1 contrast against surface-0)
    And "--text-soft" is "#71717a"
    And "--glass-dock-bg" is "rgba(18, 18, 20, 0.85)"

  Scenario: Preserving domain colors and dynamic primary ramp
    Given dark mode is active
    Then domain colors (vital, activity, hydrate, fasting, circadian, sleep, success) remain unchanged
    And the dynamic OkLCH primary ramp (oklch(0.70 0.19 var(--accent-hue))) renders cleanly on neutral surfaces without blue hue clash
```

## 4. Out of Scope

- Light mode changes (light mode remains clean paper/white).
- Changes to categorical Okabe-Ito colorblind palette.
