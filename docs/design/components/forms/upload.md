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

**Related:** `btn.md`, `icon.md`, `progress-bar.md`, `chip.md`, `modal.md`

## Visual Design

### Appearance
- **Drop zone:** `2px dashed --color-slate-200`, `--radius-md`, centered content, min-height 120px, cursor pointer
- **Icon:** 40px, `--color-slate-400`
- **Label:** `--font-label-md`, `--color-slate-600`, margin-top 8px
- **Hint:** `--font-body-sm`, `--color-slate-400`, margin-top 4px
- **File list/preview:** below drop zone, gap 8px

### States

| State | Border | Background | Icon Color |
|-------|--------|------------|------------|
| Idle | `2px dashed --color-slate-200` | transparent | `--color-slate-400` |
| Drag-over | `2px solid --color-primary` | `--color-primary-50` | `--color-primary` |
| File selected | `2px solid --color-slate-300` | `--color-slate-50` | `--color-slate-500` |
| Uploading | `2px solid --color-slate-300` | `--color-slate-50` | spinner 24px |
| Complete | `2px solid --color-tertiary-300` | `--color-tertiary-50` | `--color-tertiary-500` (checkmark) |
| Error | `2px solid --color-error-300` | `--color-error-50` | `--color-error-500` |

### Preview Items
- Image thumbnail: 48×48px, `--radius-sm`, `object-fit: cover`
- File icon: 48px generic file type icon
- Filename + size: `--font-body-sm`, to the right of preview
- Remove button: × 20px, `--color-slate-400`, top-right of preview. Hover: `--color-error-500`

### Progress Bar
- Below file list. Height: 4px. Color: `--color-primary`. See `progress-bar.md`.

### Sizes
| Size | Min Height | Icon | Context |
|------|-----------|------|---------|
| Standard | 120px | 40px | Modal, card |
| Inline | 44px | 20px | Compact forms |

### Responsive
- Standard: min-height 80px on mobile
- Inline: full-width
