# Color Picker

**Anatomy:** Native `<input type="color">` with 44×80px dimensions. Opens OS color picker dialog.

**States:** Default (shows current color) · Focus (primary ring)

**Appearance:** Padding: 4px. Border: 1px slate-300. Radius: md. Cursor: pointer.

**Value:** Hex string (#RRGGBB). Used for metric type colors in settings.

**Do:** Use for custom color selection · Integrate with form layout · Show current color preview

**Don't:** Style beyond recognition (native OS picker is accessible) · Omit label

**Accessibility:**
- `<input type="color">` with associated `<label>`
- Native picker has built-in keyboard accessibility
- Color preview: shows current value visually
- Focus: visible ring

**Related:** `input.md`, `form-layout.md`
