# User Menu

**Tokens:** Reuses `--nav-*` tokens plus `--btn-danger-text`

**Anatomy:** Avatar trigger (36px, rounded-full) + Dropdown (user info header + action items + divider + logout)

**States:** Closed · Open (dropdown visible, lg shadow, 12px radius)

**Trigger:** Avatar with optional notification dot.

**Dropdown contents:** Display name + email (header, non-clickable), action links, hr divider, Logout (error-700, bold).

**Logout:** Explicitly styled in error color. Uses `hx-boost="false"` to force full-page navigation (clears cookies properly).

**Do:** Show user identity in trigger · Provide clear Logout · Use hx-boost=false for auth state changes

**Don't:** Place settings here (use dedicated Settings page) · Omit email for multi-account clarity
