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
