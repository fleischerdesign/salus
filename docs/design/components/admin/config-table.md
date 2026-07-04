# Config Table (Admin)

**Anatomy:** data-grid table with columns: Key, Value, Source (chip), Category

**Secret values:** Masked by default (••••••••). Reveal button (eye icon, hx-get) shows value inline.

**Source chip:** ENV → neutral chip ("ENV"). DB → primary chip ("DB").

**Editing:** Click config key opens edit form below row. Inline form with input + Save button. Secret keys editable; non-secret keys directly editable in input.

**Do:** Mask secret values · Show source context · Use inline editing

**Don't:** Expose secret values by default · Show raw JSON values · Omit save feedback
