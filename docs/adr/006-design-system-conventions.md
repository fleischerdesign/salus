# 6. Design-system conventions: type scale, contrast tokens, interaction states

- Status: Proposed
- Date: 2026-08-13

## Context

The token foundation (colors, radius, shadow, duration, easing, z-index) existed
in `app.css` but was inconsistently applied:

- **No type scale** — 13+ ad-hoc sizes (`text-[8px]` … `text-[28px]`) alongside
  the Tailwind defaults, no named steps for labels/captions.
- **No contrast tokens** — `text-white` was hardcoded on `bg-primary/success/
  error/warning` fills. Since the semantic ramps invert in dark mode, the fill
  becomes light while the text stays white → invisible (the reported
  PageHeader hover bug).
- **Dead tokens** — `--color-metric-*`, most `--ease-*`, `--tracking-label`,
  and most `--z-*` were defined but never wired; raw `z-500`/`z-[501]`/`z-2000`
  and raw `duration-500` were used instead.
- **Raw colors bypassed tokens** — `emerald/amber/rose/red/indigo/cyan` used
  where `success/warning/error/primary` tokens existed, requiring hand-written
  `dark:` patches and breaking colorblind/accent in those spots.
- **Copy-paste drift** — the primary page action button existed in three
  inconsistent variants (missing/extra `active:`/`disabled:`/`transition-*`),
  and `Card`/`ChromeCard` were near-duplicates.
- **Ad-hoc interaction conventions** — four different hover backgrounds
  (`surface-50/100/200/0`), no focus ring on `Toggle`, no `cursor-not-allowed`
  on disabled buttons.
- **Broken heading outline** — `h1` only inside `PageHeader`, with `h2/h3/h4`
  used ad hoc in pages.

## Decision

Adopt the following conventions as the single source of truth:

1. **Type scale** — use Tailwind's built-in steps (`text-xs` … `text-3xl`) plus at most
   one caption size (`text-[10px]`). Custom `--text-*` tokens are not used
   (Tailwind v4 does not generate named font-size utilities from `@theme`);
   every `text-[Npx]` maps to the nearest built-in step, and body text below
   12px is eliminated (accessibility).
2. **Contrast tokens** — `--color-on-primary`, `--color-on-success`,
   `--color-on-error`, `--color-on-warning` (white in light mode, dark in dark
   mode; `on-warning` dark in both). Any text on a semantic fill uses `text-on-*`,
   never `text-white`.
3. **Semantic colors only** — components use `success/warning/error/primary/
   surface` tokens; raw Tailwind palette colors are reserved for data-viz scales
   only. No hand-written `dark:` patches on raw colors.
4. **Z-index & duration** — z-index uses Tailwind's bare-value scale on a coherent
   ladder (`z-40` popover, `z-50` dropdown, `z-60` tooltip, `z-200` sticky,
   `z-300` overlay, `z-400` drawer, `z-500` modal, `z-2000` toast); durations use
   the `--duration-*` tokens (no raw `duration-N`).
5. **Interaction states** — one hover convention (`hover:bg-surface-100` for
   list/row items, `hover:bg-primary-50` for primary affordances); every
   interactive element has a visible focus ring; disabled elements set
   `cursor-not-allowed`.
6. **Component reuse** — shared interactive elements are components
   (`PageHeaderAction`, one `Card` implementation), not copy-pasted class
   strings.
7. **Heading outline** — `h1` (page, via `PageHeader`) → `h2` (section) →
   `h3` (card), consistently.

## Consequences

- `app.css` keeps only tokens that are actually used; dead tokens are removed.
- `text-white` on semantic fills is replaced by `text-on-*` (~30 call sites).
- Raw `emerald/amber/rose/red/indigo/cyan` are mapped to tokens (~19 files).
- `PageHeaderAction` component replaces ~15 copy-pasted action buttons;
  `ChromeCard` is folded into `Card` (or removed) to eliminate duplication.
- The dashboard's hardcoded metric colors use the real metric preference color
  or the accent token.
- Verification includes a manual pass in light, dark, and colorblind modes.

## Alternatives considered

- **Full custom token editing / larger type scale** — rejected: more tokens do
  not improve consistency; a small, strict scale is more maintainable.
- **Introduce a separate `info` token** — rejected: "info" usage is mostly
  metric-specific (→ metric color) or a hint (→ accent); a 4th semantic color is
  underused.
