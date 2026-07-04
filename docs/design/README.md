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
├── README.md                  ← This file
├── branding.md                ← Brand personality, philosophy, audience
├── tokens/                    ← Design tokens (canonical values)
│   ├── colors.md
│   ├── typography.md
│   ├── spacing.md
│   ├── elevation.md
│   └── motion.md
├── components/                ← Component specifications
│   ├── core/                  (button, input, modal, card, alert, ...)
│   ├── navigation/            (top-app-bar, nav-dropdown, user-menu, ...)
│   ├── forms/                 (form-layout, toggle, search, date-picker, ...)
│   ├── data/                  (table, chip, progress-bar, pagination, ...)
│   ├── feedback/              (toast, confirmation-dialog, tooltip)
│   ├── dashboard/             (widget, viz-*)
│   ├── sharing/               (peer-card, invite-modal, ...)
│   ├── workout/               (active-session, plan-card, ...)
│   ├── onboarding/            (wizard)
│   └── admin/                 (user-table, config-table, ...)
└── patterns/                  ← UX patterns
    ├── layout.md
    ├── forms.md
    └── loading.md
```

## File Count

| Directory | Files |
|-----------|-------|
| `tokens/` | 5 |
| `components/core/` | 8 |
| `components/navigation/` | 7 |
| `components/forms/` | 6 |
| `components/data/` | 10 |
| `components/feedback/` | 3 |
| `components/dashboard/` | 1 |
| `components/sharing/` | 4 |
| `components/workout/` | 4 |
| `components/onboarding/` | 1 |
| `components/admin/` | — (TBD) |
| `patterns/` | 3 |
| **Total** | **52** |

## Maintenance Rule

When adding a new component, create its spec file in the appropriate `components/{group}/` directory. Follow the schema:

```markdown
# Component Name

**Tokens:** --token-1, --token-2, ...

**Anatomy:** Element descriptions.

**States:** Default · Hover · Focus · Active · Disabled · Error · Loading · Empty (as applicable)

**Sizes:** Standard · Small · etc. (as applicable)

**Do:** Best practices.

**Don't:** Anti-patterns.
```
