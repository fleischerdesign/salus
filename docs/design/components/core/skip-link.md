# Skip Link

> Status: **Design spec only — not yet implemented.** WCAG 2.4.1 requirement.

**Anatomy:** Hidden link that becomes visible on first Tab press. "Skip to main content"

**States:** Hidden (offscreen, visually hidden) · Focused (becomes visible at top of page)

**Appearance:** When focused: slides down from top, slate-900 bg, slate-50 text, body-md font, 12px 24px padding, centered text, z-tooltip (500). Clicking moves focus to `<main id="main-content">`.

**HTML:** First focusable element after `<body>`. `<a href="#main-content" class="sr-only focus:...">`

**Accessibility:** Implement as first focusable element after `<body>`. Target must have `id="main-content"` on the main content container. When activated, focus moves to target (not just scroll — `element.focus()` with `tabindex="-1"`). Link text describes purpose: "Skip to main content". Focus ring must be visible when focused (inherits focus-ring tokens).

**Do:** Implement as first focusable element · Move focus to main content · Make visible on focus

**Don't:** Omit (WCAG violation) · Make permanently visible · Scroll instead of moving focus

**Token Values:**
| Token | Value |
|-------|-------|
| --skip-link-bg | `{colors.slate-900}` |
| --skip-link-text | `{colors.slate-50}` |
| --skip-link-font | `var(--font-body-md)` |
| --skip-link-z-index | `var(--z-tooltip)` |

**Related:** `focus-ring.md`

## Visual Design

### Appearance
- **Offscreen (default):** `position: absolute; top: -100%; left: -100%` (completely hidden)
- **Focused:** `position: fixed; top: 8px; left: 50%; transform: translateX(-50%)`, `--color-slate-900` bg, `--color-slate-50` text, `--font-body-md`, padding 12px 24px, `--radius-md`, `--shadow-lg`, `--z-tooltip` (500)
- **Focus ring:** Standard focus ring on focus

### States
| State | Position | Visibility |
|-------|---------|------------|
| Hidden (default) | Offscreen | Not visible, not in visual flow |
| Focused (Tab) | Fixed top-center | Visible, slide-down animation 150ms ease-out |
| Activated (click/Enter) | Moves focus to `#main-content` | Hidden again |

### Animation
Appear on focus: slide-down 150ms ease-out (translateY -100% → 0) + fade-in.
Disappear on blur: instant.

### Spacing
- Padding: 12px 24px
- Top offset: 8px from viewport top
- Radius: `--radius-md` (8px)
