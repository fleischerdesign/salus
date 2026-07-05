# Wizard

**Anatomy:** Modal backdrop + Step indicator (dots) + Step content (icon + title + description + body) + Footer (Back + Next/Skip/Finish)

**States:** In-progress (step 1,2,3) · Success (completed)

**Step indicator:** 3 dots, active dot is primary-filled, inactive dots are slate-300.

**Navigation:** Back button (disabled on first step). Next button (validates form). Skip (optional, skips non-required step). Done (closes wizard).

**Body:** Step-specific content loaded via HTMX. Token generation → Entry creation → Goal creation.

**Success state:** Large success icon (48px, tertiary), congratulations message, dismiss button.

**Animation:** Step content slides in from right (250ms ease-out). Success state fades in.

**Do:** Keep steps ≤5 · Show progress indicator · Validate before advancing · Allow skip for optional steps

**Don't:** Force linear progression when optional · Omit back button · Show success before server confirms

**Responsive:** Modal full-width on mobile with 16px margin. Step content scrollable within modal if content exceeds viewport. Button layout stacks vertically on narrow screens.

**Accessibility:**
- Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Step indicator: list with `aria-current="step"` on active step
- Step content: `aria-live="polite"` when step changes (content swap via HTMX)
- Next/Back: labeled clearly with direction + step context
- Success state: `aria-live="assertive"` announcing completion
- Focus moves to first focusable element on each new step

**Composition:** Modal (Backdrop + Card) containing: Step indicator (dots) + Step content (icon + title + desc + body) + Footer (Back + Next/Skip/Finish). Step body loaded via HTMX.

**Related:** `modal.md`, `step-indicator.md`, `btn.md`, `icon.md`, `empty-state.md`, `form-layout.md`

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
