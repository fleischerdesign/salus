# Plugin Table (Admin)

**Anatomy:** Card header (title + "Upload Plugin" button) + Plugin cards/rows with: Name, Version, Status (chip), Actions

**Status chip:** LOADED → success chip. INACTIVE → neutral chip.

**Actions:** Toggle (Enable/Disable, hx-post), Uninstall (hx-delete with hx-confirm).

**Upload:** Modal with file drop zone (ZIP only). Click or drag-and-drop. hx-post for upload.

**Toggle:** Instant status change via HTMX. Button label toggles (Enable → Disable).

**Uninstall:** Destructive. Removes plugin files and DB records. Requires confirmation.

**Do:** Show version · Use hx-confirm for uninstall · Support drag-and-drop upload

**Don't:** Omit confirmation for destructive actions · Block UI during upload · Forget error feedback on invalid ZIP
