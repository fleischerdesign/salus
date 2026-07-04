# File Upload

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Drop zone area (dashed border, icon + label + hint text) + File input (hidden) + Optional preview + Optional progress bar

**States:** Idle (dashed border, slate-200) · Drag-over (primary border, primary-50 bg) · File selected (shows filename + size) · Uploading (progress bar) · Complete (success chip) · Error (error chip + retry button)

**Interaction:** Click to open file dialog. Drag-and-drop from OS. Accept attribute restricts file types.

**Sizes:** Standard (full-width in modal/card, min-height 120px). Inline (compact, single-line area).

**Preview:** Image files: thumbnail. Other files: icon + filename + size. Remove button (X) next to each file.

**Do:** Support drag-and-drop · Show file type restrictions · Show upload progress · Allow file removal before upload

**Don't:** Accept files silently without visual feedback · Omit file type validation · Show no progress during upload · Allow upload without confirming file selection

**Accessibility:**
- `<input type="file">` hidden, triggered by label/button
- Drop zone: `role="button"`, `tabindex="0"`, `aria-label="Upload file"` or "Click or drag file to upload"
- Drag-over: `aria-dropeffect="copy"`
- File list: each file with `aria-label` describing filename and size
- Remove button: `aria-label="Remove {filename}"`
- Upload progress: `aria-valuenow` on progress bar

**Token Values:**
| Token | Value |
|-------|-------|
| --upload-zone-border | `2px dashed {colors.slate-200}` |
| --upload-zone-drag-border | `2px solid {colors.primary}` |
| --upload-zone-drag-bg | `{colors.primary-50}` |
| --upload-zone-min-height | `120px` |
| --upload-zone-icon-size | 40px |
| --upload-preview-size | 48px |
| --upload-progress-color | `{colors.primary}` |

**Responsive:** Full-width. Min-height reduces to 80px on mobile.

**Related:** `button.md`, `icon.md`, `progress-bar.md`, `chip.md`, `modal.md`
