# Tabbed Sidebar

**Tokens:** Reuses `--nav-*` tokens

**Anatomy:** Sidebar (240px, right-border) + Content area (flex-1)

**Sidebar links:** label-md font, full-width, 3px left border (transparent → primary when active). Hover: slate-50 bg.

**Responsive (<900px):** Sidebar becomes horizontal scrollable tab row above content instead of left panel.

**States:** Default · Active (primary-50 bg, 3px primary left-border, primary text)

**Do:** Use for settings/admin sections · Keep labels short · Maintain consistent sidebar width

**Don't:** Use for primary navigation (use TopAppBar) · Mix navigation styles on same page
