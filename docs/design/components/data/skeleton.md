# Skeleton Loader

**Anatomy:** Animated placeholder rectangles matching expected content shape.

**States:** Active (pulsing 1.8s animation) · Replaced (when content loads)

**Animation:** `skeleton-pulse` keyframe: opacity 0.4 → 0.75 → 0.4, 1.8s cubic-bezier.

**Variants:**
- Text line: 100% width, 14px height, rounded-sm
- Card: full card dimension, rounded-md
- Widget: widget-chrome + placeholder body
- Chart: rectangular area with subtle border

**Do:** Use during initial load · Match skeleton shape to expected content · Show skeleton in dashboards, feeds, tables

**Don't:** Show skeleton for <300ms loads (flash) · Use skeleton for error states · Mix skeleton and real content in same area

**Accessibility:**
- `aria-busy="true"` on skeleton container until content loads
- `aria-hidden="true"` on skeleton shapes (they convey no information)
- After content loads: remove `aria-busy`, swap skeleton for real content
- Screen reader may announce "Loading" while aria-busy is true

**Related:** `spinner.md`, `empty-state.md`, `loading-btn.md`

## Visual Design

### Appearance
- **Background:** `--color-slate-200`
- **Animation:** `skeleton-pulse` keyframe (opacity 0.4→0.75→0.4, 1.8s ease-in-out infinite)
- **Prevents interaction while active**

### Shapes

| Shape | Height | Width | Radius | Use |
|-------|--------|-------|--------|-----|
| Text line | 14px | 100% | `--radius-sm` | Paragraphs, labels |
| Heading | 20px | 60% | `--radius-sm` | Card titles |
| Avatar | 40px | 40px | `--radius-full` | User avatars |
| Card | full card | full card | `--radius-md` | Whole card placeholder |
| Chart bar | variable | 100% | `--radius-xs` | Bar chart loading |
| Widget body | 100px | 100% | `--radius-md` | Widget content |

### States
| State | Visual |
|-------|--------|
| Active (loading) | Pulsing 1.8s animation, `aria-busy="true"` |
| Replaced (loaded) | Swapped out for real content, `aria-busy` removed |

### Usage Rules
- Don't show for loads < 300ms (flash)
- Match skeleton shape to expected content
- One skeleton per loading container
- Never mix skeleton + real content in same area
