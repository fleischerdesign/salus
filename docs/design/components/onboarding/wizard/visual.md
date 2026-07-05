## Visual Design

### Modal
Max 440px, centered. Step indicator at top (3 dots, 8px, gap 8px). Step content below. Footer at bottom.

### Step Indicator
See `step-indicator.md`. Dot variant: 8px circles, 8px gap, centered.

### Step Content
- **Icon:** 48px, centered, colored by step context (primary for setup, tertiary for success)
- **Title:** `--font-headline-md` (20px, 600), centered, 16px below icon
- **Description:** `--font-body-sm`, `--color-slate-500`, centered, 8px below title
- **Body:** form fields or token display, 24px below description

### Footer
- Back (left): ghost button, disabled on step 1
- Next/Finish (right): primary button
- Skip (optional): ghost link, right of back
- Gap: 8px between buttons

### Animation
- Step transition: content slides in from right 250ms ease-out
- Success: large check icon (48px, tertiary), fade-in 300ms

### Spacing
- Modal padding: 32px
- Step indicator↔Content: 24px
- Content↔Footer: 24px
