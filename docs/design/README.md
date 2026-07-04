# Salus Design System — Documentation Index

> **Root spec:** [`DESIGN.md`](../../DESIGN.md) — YAML front matter with canonical token values + Brand & Principles.
>
> **Audit:** [`AUDIT.md`](../../AUDIT.md) — Comprehensive issue tracker for codebase quality.

---

## Quick Start — Which docs to load?

| Task | Load these files |
|------|-----------------|
| Understanding the brand | `branding.md` |
| Getting token values | `tokens/colors.md`, `tokens/typography.md`, etc. |
| Building a new component | Component file in `components/{group}/` + relevant `tokens/` |
| Fixing layout/spacing | `patterns/layout.md`, `tokens/spacing.md` |
| Implementing a form | `components/core/input.md`, `components/forms/form-layout.md`, `patterns/forms.md` |
| Adding loading states | `patterns/loading.md`, `components/data/skeleton.md`, `components/data/spinner.md` |
| Working on navigation | `components/navigation/top-app-bar.md` + others |
| CSS refactoring | All `tokens/*.md` + relevant `components/*.md` |

---

## Directory Structure

```
docs/design/
├── README.md
├── branding.md               ← Brand personality, philosophy, audience
├── tokens/                   ← Design tokens (canonical values)
│   ├── colors.md             (6 color families × 10 steps, surface, metric, rank)
│   ├── typography.md         (13 type scale entries, utility classes)
│   ├── spacing.md            (8 spacing steps, utility classes)
│   ├── elevation.md          (radius, shadows 0-4, z-index)
│   └── motion.md             (breakpoints, durations, easings, transitions)
├── components/               ← Component specifications (unique components only)
│   ├── core/                 (10)  button, input, modal, card, alert, ...
│   ├── navigation/           (7)   top-app-bar, nav-dropdown, user-menu, ...
│   ├── forms/                (7)   form-layout, toggle, search, date-picker, ...
│   │                               file-upload
│   ├── data/                 (10)  table, chip, badge, progress-bar, pagination,
│   │                               skeleton, spinner, chart-tooltip, secret-reveal
│   ├── feedback/             (3)   toast, confirmation-dialog, tooltip
│   ├── dashboard/            (8)   widget, viz-number, viz-progress, viz-sparkline,
│   │                               viz-pills, viz-bar, viz-candlestick, kpi-card
│   ├── sharing/              (4)   peer-card, pending-invitation, invite-modal,
│   │                               federation-status
│   ├── workout/              (4)   active-session, plan-card, exercise-item,
│   │                               autoregulation-set
│   └── onboarding/           (1)   wizard
└── patterns/                 ← UX patterns
    ├── layout.md             (grid system, container, responsive)
    ├── forms.md              (validation, error handling, progressive enhancement)
    └── loading.md            (skeleton, spinner, HTMX indicators)
```

## Component Catalog (61 unique components)

### Core (10)
| Component | Status | Description |
|-----------|--------|-------------|
| Button | ✅ Implemented | Primary, Secondary, Ghost, Danger, Small, Icon |
| Input | ✅ Implemented | Text, Select, Textarea, Color |
| Checkbox | ✅ Implemented | Standard checkbox |
| Card | ✅ Implemented | Content container with header |
| Modal | ✅ Implemented | Dialog overlay |
| Alert | ✅ Implemented | Success, Error inline messages |
| Empty State | ✅ Implemented | Icon + title + description + CTA |
| Auth Form | ✅ Implemented | Login/Register card with provider buttons |
| Loading Button | 📐 Design spec | Button with spinner + success/error states |
| Copy to Clipboard | 📐 Design spec | Copy button with feedback |

### Navigation (7)
| Component | Status | Description |
|-----------|--------|-------------|
| TopAppBar | ✅ Implemented | Sticky header with nav links |
| Nav Dropdown | ✅ Implemented | Hover-based dropdown menu |
| User Menu | ✅ Implemented | Avatar trigger, dropdown with logout |
| Tabbed Sidebar | ✅ Implemented | Settings/Admin section navigation |
| Day Navigator | ✅ Implemented | Date navigation with prev/next |
| Breadcrumbs | 📐 Design spec | Path trail navigation |
| Drawer | 📐 Design spec | Slide-out panel for mobile |

### Forms (7)
| Component | Status | Description |
|-----------|--------|-------------|
| Form Layout | ✅ Implemented | form-stack, form-row, form-actions |
| Radio Group | ✅ Implemented | Single-select button group |
| Toggle / Switch | 📐 Design spec | On/off switch |
| Search Input | 📐 Design spec | Search with debounce + clear |
| Date Picker | 📐 Design spec | Calendar dropdown |
| File Upload | 📐 Design spec | Drag-and-drop + progress |
| Chip Row | ✅ Implemented | Inline chip selection group |

### Data (10)
| Component | Status | Description |
|-----------|--------|-------------|
| Table | ✅ Implemented | Data grid with header, hover, empty |
| Chip (Status) | ✅ Implemented | Success, Warning, Error, Neutral |
| Badge (Notification) | 📐 Design spec | Numeric notification dot |
| Progress Bar | ✅ Implemented | Track + fill with percentage |
| Skeleton | ✅ Implemented | Animated placeholder shapes |
| Spinner | ✅ Implemented | Rotating ring indicator |
| Chart Tooltip | ✅ Implemented | Floating data detail on hover |
| Pagination | 📐 Design spec | Page controls with ellipsis |
| Secret Reveal | ✅ Implemented | Masked value → eye toggle → reveal |
| Key Value | ✅ Implemented | Label + value display pattern |

### Feedback (3)
| Component | Status | Description |
|-----------|--------|-------------|
| Toast | 📐 Design spec | Transient corner notification |
| Confirmation Dialog | 📐 Design spec | Modal confirm for destructive actions |
| Tooltip | 📐 Design spec | Hover info popup |

### Dashboard (8)
| Component | Status | Description |
|-----------|--------|-------------|
| Widget | ✅ Implemented | Dashboard grid item with chrome |
| Viz: Number | ✅ Implemented | Value + unit + delta |
| Viz: Progress | ✅ Implemented | Ring/bar with target |
| Viz: Sparkline | ✅ Implemented | Mini trend chart |
| Viz: Pills | ✅ Implemented | Zone/stage breakdown chart |
| Viz: Bar | ✅ Implemented | Segmented composition bar |
| Viz: Candlestick | ✅ Implemented | OHLC chart with labels |
| KPI Card | 📐 Design spec | Compact metric summary card |

### Sharing (4)
| Component | Status | Description |
|-----------|--------|-------------|
| Peer Card | ✅ Implemented | Connection card with metrics |
| Pending Invitation | ✅ Implemented | Accept/decline inline |
| Invite Modal | ✅ Implemented | QR code + copy link |
| Federation Status | 📐 Design spec | Remote sync status indicator |

### Workout (4)
| Component | Status | Description |
|-----------|--------|-------------|
| Active Session | ✅ Implemented | Live workout logging |
| Plan Card | ✅ Implemented | Training plan with exercise list |
| Exercise Item | ✅ Implemented | Equipment + muscles + video |
| Autoregulation Set | ✅ Implemented | Set logging with 1RM calc |

### Onboarding (1)
| Component | Status | Description |
|-----------|--------|-------------|
| Wizard | ✅ Implemented | Multi-step guided setup |

---

## Anti-Redundancy Rules

1. **One file per unique visual component.** No "Admin User Table" spec — that's just a `Table` with specific columns.
2. **Columns/configurations are NOT components.** They belong in page documentation or router comments.
3. **If two files describe the same anatomy with different data, they're redundant.** Merge or delete.
4. **NEW components are marked `📐 Design spec`** — they define future behavior but don't exist in code yet.

---

## Maintenance Rule

When adding a new component, create its spec file in the appropriate `components/{group}/` directory:

```markdown
# Component Name

**Tokens:** --token-1, --token-2, ...

**Anatomy:** Element descriptions.

**States:** Default · Hover · Focus · Active · Disabled · Error · Loading · Empty

**Sizes:** Standard · Small · etc. (as applicable)

**Do:** Best practices.

**Don't:** Anti-patterns.
```
