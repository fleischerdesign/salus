---
name: Salus Health System
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
  tertiary: '#005338'
  on-tertiary: '#ffffff'
  tertiary-container: '#006e4b'
  on-tertiary-container: '#67f4b7'
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
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  metric-display:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  max-width: 960px
  gutter: 1.5rem
  container-padding: 2rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style

The design system is centered on the principles of **Clinical Clarity** and **Personal Warmth**. As a health data platform, the interface must prioritize trust, precision, and ease of use. The design style follows a **Modern Corporate** aesthetic with a lean toward **Minimalism**, ensuring that dense medical data remains legible and non-intimidating.

The emotional response should be one of "calm control." By utilizing generous whitespace, a structured grid, and a restricted color palette, the system reduces cognitive load, allowing users to focus on their health metrics without distraction. The aesthetic is light, airy, and professional, echoing a modern digital clinic.

## Colors

The palette is anchored by **Indigo-600 (#4f46e5)**, chosen for its association with wisdom and professional stability. This is the primary action color.

- **Primary (Indigo):** Used for primary buttons, active navigation states, and branding.
- **Secondary (Sky):** Used for informational accents and "Sleep" or "Hydration" metrics.
- **Tertiary (Emerald):** Reserved for positive health trends, "Nutrition," and "Success" states.
- **Neutral (Slate/Gray):** Used for secondary text, borders, and UI scaffolding.

A semantic color system should be applied to health metrics:
- **Heart Rate:** Rose-500
- **Steps/Activity:** Amber-500
- **Sleep:** Indigo-400
- **Nutrition:** Emerald-500

Backgrounds remain consistently light (#F8FAFC) to maintain an airy feel, with subtle borders (#E2E8F0) providing necessary structure without the heaviness of shadows.

## Typography

The design system utilizes **Inter**—a highly legible system sans-serif stack—to ensure clarity across all data-dense dashboards. The typography is systematic and functional.

- **Headlines:** Use tight letter-spacing and bold weights to establish a clear hierarchy.
- **Body:** Optimized for reading health reports and insights with a comfortable 1.5x line height.
- **Labels:** Small caps are used for section headers within cards to differentiate them from data values.
- **Metrics:** A specific `metric-display` style is provided for high-impact numbers (e.g., daily step counts or heart rate), emphasizing data over prose.

## Layout & Spacing

This design system employs a **Fixed Grid** philosophy for desktop to ensure a focused, readable experience. The content is centered with a **960px max-width** to prevent line lengths from becoming too long, which is critical for health data interpretation.

### Breakpoints
- **Desktop:** 960px max-width, 12-column grid within the container.
- **Tablet:** Fluid width with 40px side margins, 8-column grid.
- **Mobile:** Fluid width with 16px side margins, 4-column grid.

### Spacing Rhythm
A strict 8px (0.5rem) baseline grid is used. Spacing between cards should be consistent at `stack-lg` (32px), while internal card padding should follow `stack-md` (16px) or `stack-lg` (24px) depending on the content density.

## Elevation & Depth

To maintain the "clean and professional" health aesthetic, the design system avoids heavy shadows and physical metaphors. Instead, it relies on **Low-contrast outlines** and **Tonal layers**.

- **Cards:** White backgrounds (#FFFFFF) with a 1px solid border (#E2E8F0). No shadow is used for standard cards.
- **Hover States:** Elements may gain a subtle "Indigo" tinted shadow (4% opacity) or a slightly darker border (#CBD5E1) to indicate interactivity.
- **Modals:** Use a heavy backdrop blur (8px) with a soft, diffused shadow to pull focus away from the dashboard without cluttering the visual field.
- **Section Headers:** Use a light gray background (#F1F5F9) to distinguish header rows from content rows in lists.

## Shapes

The shape language is **Soft** and clinical. 

- **Cards & Inputs:** Use a 4px (0.25rem) radius for a precise, professional look.
- **Primary Buttons:** Can utilize a slightly larger radius (8px) to make them appear more touch-friendly and distinct from data containers.
- **Progress Bars:** Use fully rounded ends (pill-shaped) to represent "fluid" health data like daily goals or nutrient intake.

## Components

### Buttons
- **Primary:** Solid Indigo background, white text. No gradient.
- **Secondary:** White background, Indigo border and text.
- **Ghost:** No border or background, Indigo text. Used for less frequent actions like "Learn More."

### Health Metric Cards
- The hero of the dashboard. Contains a `label-caps` title, a `metric-display` value, and a small sparkline or trend indicator.
- Top border-accent (2px) color-coded by metric type (e.g., Red for Heart Rate).

### Lists & Tables
- Used for historical data. Clean, 1px horizontal dividers only.
- Alternating row colors are avoided; use hover states instead.

### Inputs & Selects
- 1px Slate-200 border, 4px radius.
- On focus: 1px Indigo-600 border with a 2px Indigo-100 outer glow (soft ring).

### Progress & Status
- **Progress Bars:** Thin (8px height) with a light gray track.
- **Chips:** Small, rounded-full badges used for status (e.g., "In Range," "High"). Backgrounds should be highly desaturated versions of the status color (e.g., Success = Light Green background, Dark Green text).

### Icons
- Use a cohesive set of **24px stroke-based icons** (e.g., Lucide or Feather). Strokes should be 1.5px or 2px thick to match the professional weight of the Inter typeface.