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
