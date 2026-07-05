# Theme Toggle

**Anatomy:** Radio group of 3 options: System (auto) · Light · Dark. Each option shows icon + label.

**Icons:** System: `brightness_auto`. Light: `light_mode`. Dark: `dark_mode`.

**States:** Selected (primary bg, white text. See radio-group.md) · Unselected

**Implementation:** `hx-post` to settings endpoint. `data-theme` attribute updated on `<html>`. No page reload — CSS custom properties switch theme.

**Storage:** Cookie or localStorage. Default: `data-theme="system"`.

**Do:** Offer all 3 modes · Apply immediately · Persist selection · Use recognizable icons

**Don't:** Require page reload · Omit system/auto option · Use toggle switch (3 options, not binary)

**Accessibility:**
- `<fieldset>` + `<legend>` for the radio group
- Each option: `<input type="radio">` + `<label>` with matching `for`/`id`
- Icons: `aria-hidden="true"` (label text provides the accessible name)
- Immediate feedback: `aria-live="polite"` announcing theme change

**Related:** `radio-group.md`, `language-switcher.md`, `icon.md`

## Visual Design

### Appearance
- **Layout:** Radio group (horizontal), gap 8px
- **Option:** 36×36px, `--radius-md`, ghost style. Icon: 20px. Selected: `--color-primary` bg, `--color-on-primary` text
- **Icons:** System: `brightness_auto`, Light: `light_mode`, Dark: `dark_mode`
- **Labels:** hidden (icon-only), tooltip on hover

### States
| State | Background | Icon Color |
|-------|-----------|------------|
| Default (unselected) | transparent | `--color-slate-500` |
| Hover (unselected) | `--color-slate-100` | `--color-slate-700` |
| Selected | `--color-primary` | `--color-on-primary` |
| Focus | Standard focus ring | — |

### Spacing
- Gap: 8px between options
- Option size: 36×36px, icon: 20px
- Group padding: 4px
