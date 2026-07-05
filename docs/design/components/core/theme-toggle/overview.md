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
