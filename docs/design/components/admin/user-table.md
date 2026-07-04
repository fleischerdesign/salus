# User Table (Admin)

**Anatomy:** data-grid table with columns: Username, Email, Admin (chip), Active (chip), Joined, Actions

**Admin chip:** True → success chip ("ADMIN"). False → neutral chip ("USER").

**Active chip:** True → success chip ("ACTIVE"). False → warning chip ("INACTIVE").

**Actions:** Detail (link), Toggle Admin (hx-post), Toggle Active (hx-post), Delete (hx-post with hx-confirm).

**Delete confirmation:** Uses browser confirm dialog. Should be replaced with custom confirmation dialog.

**Do:** Show identity chips · Use hx-confirm for destructive actions · Show join date

**Don't:** Omit confirmation for delete · Show raw boolean values instead of chips · Forget hx-target for table refresh
