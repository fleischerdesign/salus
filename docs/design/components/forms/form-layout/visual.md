## Visual Design

### Patterns

| Pattern | Direction | Gap | Max Width | Use |
|---------|-----------|-----|-----------|-----|
| `.form-stack` | Vertical | 16px | 100% | Default layout |
| `.form-row` | Horizontal | 16px | 100% | 2-3 related fields |
| `.form-actions` | Horizontal, right-aligned | 8px | 100%, margin-top 8px | Submit + Cancel |
| `.input-group` | Vertical | 4px (label), 4px (hint) | 100% | Each field unit |

### States

| State | Visual |
|-------|--------|
| Default | Form interactive |
| Submitting | Form `pointer-events: none`, submit button loading (spinner + disabled) |
| Error | Alert banner (error variant) above form. Field-level errors with red text |
| Success | Redirect or inline success alert (see `alert.md`) |

### Spacing
| Gap | Value | Context |
|-----|-------|---------|
| Between form groups | 16px | Vertical stack |
| Between inline fields | 16px | Horizontal row |
| Label↔Input | 4px | Every field |
| Input↔Hint/Error | 4px | Every field |
| Form↔Actions | 8px | Above submit bar |

### Responsive
- `.form-row` collapses to vertical stack below `--bp-mobile`
- `.form-actions` buttons become full-width and stack vertically below `--bp-mobile`

### Max-width
Form container: 560px for simple forms (login, settings). Full-width for complex forms (workout planner, admin).
