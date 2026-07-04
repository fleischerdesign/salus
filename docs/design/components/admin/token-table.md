# Token Table (Admin)

**Anatomy:** data-grid table with columns: ID, User, Scopes, Created, Last Used, Revoke

**Scopes:** Chip group. Each scope shown as neutral chip.

**Last Used:** "Never" or timestamp. Muted color for never-used tokens.

**Revoke:** hx-delete with hx-confirm. Row removed via DOM on success.

**Do:** Show scope chips · Indicate never-used tokens · Confirm before revoke

**Don't:** Show full token value (only displayed once at creation) · Omit last-used info · Forget table row refresh
