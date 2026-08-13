# 5. Color & theme system: semantic tokens, categorical palette, custom accent

- Status: Proposed
- Date: 2026-08-13

## Context

Two defects and one gap motivate a unified color/theme architecture:

1. **The theme toggle is broken.** `app.css` keys dark mode on the
   `[data-theme='dark']` *attribute*, but the settings page toggles the `.dark`
   *class* (`settings/app/+page.svelte`). Nothing reads `salus_theme` on startup,
   and "system" is never re-evaluated. The toggle therefore does nothing.
2. **The "chart palette" picker is dead.** `salus_chart_palette`
   (standard/colorblind/high-contrast) is persisted but never applied. It also
   conflates two distinct concerns: colorblindness (hue) and contrast.
3. **No colorblind support.** Colors are scattered: semantic tokens
   (`--color-error/success/warning`), per-entity categorical hex (metric
   `color`, habit `color`, medication `color_hex`), hardcoded literals
   (`builders.ts`), and ad-hoc data-viz scales (mood green→red, correlation
   red/green).

There are three fundamentally different kinds of "color", which must be treated
differently:

| Kind | Examples | Nature | Tokenizable |
|---|---|---|---|
| Semantic | error / success / warning / primary / surface | fixed roles | yes (CSS tokens) |
| Categorical | metric color, habit color, source color, exercise | identity, stored as hex in entities | no (data, not CSS) |
| Data-viz scale | mood (green→red), correlation (red/green), heatmap | encode values | named scales |

## Decision

Introduce a centralized color/theme system with four components.

1. **Semantic design tokens (CSS)** — `surface`, `primary`, `error`, `success`,
   `warning` remain custom properties. A `[data-colorblind='true']` block (and a
   `[data-colorblind='true'][data-theme='dark']` block) overrides the semantic
   ramps so that status colors stay distinguishable for protan/deutan/tritan
   vision. The chosen colorblind-safe status trio is **red / amber / blue**
   (success shifts green → blue; error and warning are already distinguishable).
2. **Categorical palette (TS, single source)** — one `colors.ts` module with
   named entries, each carrying `{ normal, colorblind }` values (Okabe-Ito for
   the colorblind variant). All categorical hex — metric defaults, habit
   palette, source colors, builder literals — migrate here and are referenced by
   key. `resolveColor(key)` returns the active-mode value.
3. **Data-viz scales (TS, named)** — `scale.mood`, `scale.correlation`, etc.
   with `{ normal, colorblind }` variants, replacing inline Tailwind
   `bg-emerald/…/red` and the red/green diverging.
4. **Theme controller (`theme.svelte.ts`)** — the single orchestrator managing
   `mode` (light/dark/system) and `colorblind` (on/off), applying `data-theme`
   and `data-colorblind` attributes, persisting, and reacting to
   `prefers-color-scheme` changes. Settings delegate to it.

**Custom themes (scope):** a theme is a mapping of token-name → token-value, so
the token architecture naturally supports custom themes. Scope them to:

- **L1 — accent color** (core): one user accent; the `primary` ramp shades are
  *derived* (oklch), so contrast stays controlled.
- **L2 — curated presets** (optional): a small catalog of token sets.
- **L3 — arbitrary token editing: excluded.** Free editing of semantic tokens
  would undermine the colorblind and contrast guarantees this system exists to
  provide.

**Storage:** theme mode uses the existing `User.theme` field (already synced and
in `_SAFE_USER_UPDATE_FIELDS`). Colorblind and accent follow the same pattern as
new `User` fields (`colorblind`, `accent_color`). A dedicated `user_preference`
entity is considered but rejected for now — `User` already carries cross-device
settings (theme, locale, display_name) and adding a new synced entity for two
more fields is premature. Local mode persists device-locally as a fallback.

## Consequences

- The settings page stops writing `salus_theme`/`salus_chart_palette` ad hoc and
  delegates to the theme controller; the dead palette picker is replaced by a
  colorblind toggle.
- Phase 1 (this change) fixes the theme mechanism and adds the semantic
  colorblind tokens + toggle. Categorical palette (Phase 2), data-viz scales
  (Phase 3), and custom accent/presets (Phase 4) follow; the controller's
  storage is migrated to `User` fields in Phase 4.
- Medication `color_hex` (the only free-form color) is constrained to the
  categorical palette in Phase 2, so every color is palette-bound and
  colorblind-safe.

## Alternatives considered

- **Full custom token editing (L3)** — rejected: undermines accessibility
  guarantees and is niche; accent + presets cover real user intent.
- **Dedicated `user_preference` entity** — deferred: `User` already carries
  cross-device settings; revisit when language/unit/week-start also migrate off
  ad-hoc storage.

## Follow-ups

Open items tracked against this ADR (not implemented, do not get lost):

1. **Cloud-synced storage.** Theme mode, colorblind, and accent currently
   persist in `localStorage` (device-local). Migrate them to synced `User`
   fields (`theme` already exists; add `colorblind: bool` and
   `accent_color: str`) so they follow the user across devices:
   - Backend: extend the `User` model + Alembic migration, add the new fields to
     `_SAFE_USER_UPDATE_FIELDS`, regenerate the OpenAPI schema.
   - Frontend: the theme controller reads/writes the synced fields (with a
     device-local fallback in Local Mode), via the existing sync path.

2. **Layering.** `mergeMetricPrefs` (`db/types.ts`) now imports
   `$lib/theme/colors` → `$stores/theme.svelte`, so a data module depends on a
   UI store. Consider moving color resolution out of `mergeMetricPrefs` into the
   display layer (or pass the active mode explicitly) to keep `db/` store-free.

3. **Named palette instead of heuristics.** `resolveColor` uses a string-hash
   seed (Okabe-Ito index) and `isNeutral` uses an RGB-distance threshold. Both
   are deterministic and documented but not a curated, named color system. If
   the categorical set stabilizes, replace the hash with an explicit
   name → `{ normal, colorblind }` map per entity (metric code, habit, source),
   and drop `isNeutral` for an explicit neutral denylist.

