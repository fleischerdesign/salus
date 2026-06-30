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
  headline-xl:
    fontFamily: Manrope
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Manrope
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Manrope
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Manrope
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Manrope
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Manrope
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max-width: 1440px
  gutter: 24px
  margin-desktop: 40px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The brand personality is authoritative yet empathetic, positioning the product as a sophisticated intelligence layer for modern healthcare. The target audience includes clinicians, health administrators, and data analysts who require high-density information without cognitive fatigue.

The design style follows a **Modern Corporate** aesthetic with a lean toward **Minimalism**. It prioritizes clarity, systematic organization, and a clinical sense of precision. The UI evokes a sense of reliability and "calm intelligence" through generous whitespace, subtle tonal layering, and a restrained use of the primary brand color to highlight actionable insights rather than decorate the interface.

## Colors
The palette is rooted in a professional "Medical Indigo" (#4f46e5), which serves as the primary driver for brand identity and primary actions. 

- **Primary (Indigo):** Used for primary buttons, active navigation states, and key brand touchpoints.
- **Secondary (Sky):** Utilized for informational accents and secondary data visualizations.
- **Tertiary (Emerald):** Reserved specifically for "Success" states, positive health trends, and "System Normal" indicators.
- **Neutral (Slate):** A comprehensive scale of grays used for typography, borders, and subtle surface variations to maintain a clean, clinical backdrop.

The background remains a crisp white (#FFFFFF) or very light gray (#F8FAFC) to ensure maximum readability of medical records and data tables.

## Typography
Manrope is the exclusive typeface for this design system. It was selected for its modern, geometric construction which retains high legibility in dense data environments.

Headlines use semi-bold and bold weights with slight negative letter-spacing to appear assertive and structured. Body text utilizes standard weights for long-form medical reports. Small labels use an increased letter-spacing and medium weight to ensure they remain legible even at 12px, particularly in high-density tables and chart axes.

## Layout & Spacing
The design system utilizes a **Fixed Grid** model centered on the screen to maintain a structured, professional dashboard feel across ultra-wide monitors. 

- **Top Navigation:** A persistent `TopAppBar` spans the full width of the viewport, containing primary navigation links, search, and user profile. 
- **Content Area:** Content is housed within a max-width container of 1440px.
- **Grid:** A 12-column system is used for desktop layouts.
- **Breakpoints:**
    - Mobile (<600px): 4 columns, 16px margins.
    - Tablet (600px - 1024px): 8 columns, 24px margins.
    - Desktop (>1024px): 12 columns, 40px margins.

Spacing follows a 4px base unit, ensuring all components and layouts are mathematically aligned and harmonious.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** and extremely subtle **Ambient Shadows**. This approach minimizes visual noise, allowing data to remain the focal point.

- **Level 0 (Background):** #F8FAFC (Light Slate) – The canvas for the application.
- **Level 1 (Cards/Surfaces):** #FFFFFF – Pure white surfaces with a 1px border (#E2E8F0) and no shadow for a flat, clean look.
- **Level 2 (Hover/Active):** A soft, diffused shadow (0px 4px 12px rgba(0, 0, 0, 0.05)) is applied when a card or interactive element is hovered.
- **Level 3 (Modals/Popovers):** A more pronounced shadow (0px 12px 24px rgba(0, 0, 0, 0.1)) to lift the element above the intelligence layer.

## Shapes
The shape language uses **Rounded** (0.5rem / 8px) corners to soften the clinical nature of the product, making it feel approachable while maintaining a structured grid.

- **Standard Elements:** 8px (0.5rem) radius for buttons, input fields, and cards.
- **Large Elements:** 16px (1rem) radius for major dashboard containers and modals.
- **Data Tags/Chips:** Fully rounded (pill-shaped) to distinguish them from actionable buttons.

## Components

### TopAppBar
The primary navigation hub. It uses a white background with a thin bottom border (#E2E8F0). Links use `label-md` typography. The active state is indicated by a 2px Indigo bottom-border.

### Buttons
- **Primary:** Solid Indigo (#4f46e5) with white text.
- **Secondary:** White background with Indigo border and Indigo text.
- **Ghost:** No border or background; Indigo text. Used for low-priority actions like "Cancel".

### Tables & Data Grids
Essential for medical intelligence. Use a 48px row height for standard density. Header rows should have a subtle gray background (#F1F5F9) and use `label-sm` in all caps.

### Charts & Analytics
Charts should use a custom palette: Indigo (#4f46e5) for primary data, Sky (#0ea5e9) for secondary, and Slate (#94A3B8) for benchmarks. Grid lines should be faint (#F1F5F9).

### Cards
Dashboard cards should have a consistent 24px internal padding. Titles use `headline-md`. Cards should contain "Insights" segments—small callout boxes with light Indigo backgrounds to highlight AI-driven health suggestions.

### Input Fields
Inputs use a 1px Slate border (#CBD5E1). On focus, the border transitions to Indigo with a 2px outer glow. Labels are always positioned above the field using `label-sm`.