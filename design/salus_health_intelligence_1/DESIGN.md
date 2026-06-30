---
name: Salus Health Intelligence
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#464555'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#006591'
  on-secondary: '#ffffff'
  secondary-container: '#39b8fd'
  on-secondary-container: '#004666'
  tertiary: '#571ac0'
  on-tertiary: '#ffffff'
  tertiary-container: '#6f3dd9'
  on-tertiary-container: '#e3d5ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#c9e6ff'
  secondary-fixed-dim: '#89ceff'
  on-secondary-fixed: '#001e2f'
  on-secondary-fixed-variant: '#004c6e'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: manrope
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: manrope
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-md:
    fontFamily: inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  data-mono:
    fontFamily: jetbrainsMono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-caps:
    fontFamily: inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-margin: 24px
  gutter: 16px
  card-padding: 20px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The brand personality is authoritative yet empathetic, designed to transform complex physiological data into actionable health insights. The design system follows a **Corporate / Modern** aesthetic with a lean toward high-utility professionalism. It prioritizes clarity, precision, and trust, ensuring that critical health data is legible at a glance. The emotional response should be one of "controlled oversight"—users should feel informed and supported, never overwhelmed by the density of information.

The visual style utilizes a systematic approach: clean lines, ample whitespace to reduce cognitive load, and a strict hierarchy that distinguishes between historical data and immediate health alerts.

## Colors
The color palette is anchored by the primary Indigo, representing medical stability and institutional trust. 

### Semantic Health Tokens
- **Critical Alert (SpO2 Warning):** High-saturation Red is reserved for vital signs falling outside safe thresholds.
- **Warning (Goal Misses):** Amber is used for non-critical variances, such as falling 20% behind a daily activity goal.
- **Success:** Emerald signals goal completion and healthy biological ranges.

### Charting Palette
For time-series data, the palette uses distinct hues to prevent overlap in multi-axis charts:
- **Weight:** Indigo (Primary) for stability.
- **Steps:** Green for activity and movement.
- **Heart Rate:** Rose for cardiovascular metrics.
- **SpO2:** Deep Violet to differentiate from standard HR metrics.

## Typography
The typography system uses a tri-font approach to maximize legibility in data-dense environments.

- **Headlines (Manrope):** A modern, balanced sans-serif that provides a professional tone for dashboard summaries and section headers.
- **Body (Inter):** A highly legible, systematic font used for all UI instructions, patient notes, and general interface text.
- **Data (JetBrains Mono):** Reserved specifically for numerical values, timestamps, and vital signs. The monospaced nature ensures that fluctuating numbers (like live HR) do not cause layout shifts and remain easy to compare vertically in tables.

## Layout & Spacing
This design system utilizes a **12-column fluid grid** for desktop and a **4-column grid** for mobile. The spacing rhythm is based on a 4px baseline to allow for the fine-grained control required by complex data dashboards.

- **Dashboards:** Use a 24px outer margin with 16px gutters.
- **Data Density:** In multi-user views, vertical padding is reduced to `stack-sm` to increase the "at-a-glance" information density.
- **Information Hierarchy:** Group related metrics (e.g., Systolic/Diastolic BP) using `stack-sm`, while separating distinct metric categories (e.g., Vitals vs. Activity) with `stack-lg`.

## Elevation & Depth
Elevation is used strategically to separate the "Observation Layer" (the background) from the "Action Layer" (interactive cards and modals).

- **Surface Tiers:** The main background uses a subtle off-white/gray. Primary data cards use a pure white background with a **low-contrast outline** (1px, #e2e8f0) rather than heavy shadows to maintain a clinical, clean look.
- **Interactive Depth:** Only active elements or "pinned" vital monitors receive a soft ambient shadow (0px 4px 12px rgba(0,0,0,0.05)) to suggest they sit above the standard data grid.
- **Multi-user States:** When viewing multiple profiles, the "active" user container is highlighted with a 2px Indigo left-border stroke, rather than elevation, to maintain grid alignment.

## Shapes
The shape language is **Soft**, utilizing a 0.25rem (4px) base radius. This provides a professional, "tool-like" feel that is more approachable than sharp corners but more serious than highly rounded "consumer" apps. 

- **Data Cards:** 8px (rounded-lg) to provide a containerized feel for complex charts.
- **Inputs & Buttons:** 4px to maintain a compact, precise appearance.
- **Status Indicators:** Pills (fully rounded) are used only for status tags (e.g., "Stable", "At Risk") to differentiate them from interactive buttons.

## Components
- **Health Goal Chips:** Use semantic background tints (10% opacity) with high-contrast text. A "Missed Goal" chip uses the `alert_warning` token.
- **Time-Series Charts:** Lines should have a 2px stroke width. For SpO2 warnings, the chart area below the threshold line should be filled with a subtle `spo2_low` gradient.
- **Data Tables:** Use `data-mono` for all numerical cells. Rows should include a hover state with a subtle Indigo tint to assist in tracking data across wide screens.
- **Multi-User Avatars:** Use a 32px diameter with a status ring. A red ring indicates a "Critical Alert" for that specific user.
- **Metric Cards:** Must include a "trend" indicator (up/down arrow) and a timestamp of the last reading in `label-caps`.
- **Primary Buttons:** Solid Indigo background with white text. High-emphasis for "Start Telehealth" or "Log Vitals."