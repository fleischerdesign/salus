# Loading States — Skeletons, Spinners & HTMX Indicators

**Three loading patterns, one rule:** Never leave the UI blank while waiting.

## 1. Skeleton Loader (initial page load)

Used for dashboard widgets, analytics panels, feeds.

- Appears immediately on page load
- Matches expected content shape (text lines, card dimensions)
- Pulsing opacity animation (1.8s)
- Replaced by real content via HTMX `hx-trigger="load"`

## 2. Spinner (inline operations)

Used for button actions, content generation, inline updates.

- 16-24px rotating ring
- Replaces content area while loading
- `aria-busy="true"` on parent container

## 3. HTMX Indicator (any HTMX request)

Global or per-element indicator via `hx-indicator`.

- Opacity 0 by default, 1 during request
- `.htmx-indicator` CSS class
- `htmx:beforeRequest` shows, `htmx:afterRequest` hides

**Transition timing:**
- Show indicator after 200ms delay (avoids flash for fast responses)
- Smooth opacity transition (150ms)

**Do:** Implement all three patterns · Show feedback within 200ms · Match skeleton to content shape

**Don't:** Flash skeleton for sub-300ms loads · Leave blank area · Forget accessibility for spinners
