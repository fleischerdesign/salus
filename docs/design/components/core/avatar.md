# Avatar

**Tokens:** `--btn-icon-hover-bg`, slate colors

**Anatomy:** Circular container with user initials or icon

**Sizes:** Small (36px, label-sm font) · Large (48px, headline-md font)

**States:** Default · Hover (opacity 0.85 fade) · Active/Selected · With Status Dot (see `status-dot.md`)

**Appearance:** Slate-200 background, slate-600 text, rounded-full. Font weight: 600.

**User initial:** First character of display name or username, uppercased.

**Do:** Use for user identity · Keep consistent sizing · Add status dot for online/offline · Use aria-label for screen readers

**Don't:** Use for decorative icons · Vary size within same context · Omit alt text equivalent

**Accessibility:**
- Image avatars: `<img>` with `alt="User Name"` describing the person, not "avatar"
- Initial avatars: `role="img"` + `aria-label="User Name"`
- Status dot: `aria-label` describing status (e.g., "Online")
- Interactive avatars (clickable): `role="button"` + `tabindex="0"` + accessible name

**Related:** `status-dot.md`, `user-menu.md`, `icon.md`

## Visual Design

### Appearance
- **Background:** `--color-slate-200`
- **Text:** `--color-slate-600`, 600 weight, uppercased, centered
- **Radius:** `--radius-full`
- **Image avatar:** `<img>` with `object-fit: cover`

### Sizes
| Size | Diameter | Font |
|------|----------|------|
| SM | 36px | `--font-label-md` (13px, 600) |
| MD | 40px | `--font-body-md` (16px, 600) |
| LG | 48px | `--font-headline-md` (20px, 600) |

### States
| State | Visual | Duration |
|-------|--------|----------|
| Default | Slate-200 bg, slate-600 text | — |
| Hover (interactive) | Opacity 0.85, cursor pointer | 150ms |
| Active/Selected | `--color-primary-100` bg, `--color-primary-700` text | — |
| With status dot | 8px dot bottom-right, 2px white ring | — |

### Spacing
- Avatar↔Text (in user menu): 12px
- Status dot: 0px from bottom/right edge
