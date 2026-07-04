# Backup Table (Admin)

**Anatomy:** Card header (title + "Create Backup Now" button) + data-grid table with columns: Filename, Size, Created, Download, Delete

**Empty state:** "No backups found." with info about encryption status.

**Create Backup:** hx-post to `/admin/backups/run`. Shows loading indicator during backup.

**Download:** Direct link to backup file download.

**Delete:** hx-delete with hx-confirm. Row removed via DOM after success.

**Encryption status:** Banner above table: green if SALUS_BACKUP_PASSWORD set (E2E AES-GCM-256), amber if not set (backups disabled warning).

**Do:** Show encryption status · Provide download · Confirm before delete

**Don't:** Omit file size · Block UI during backup · Leave stale rows after delete
