# Relationship Table

**Anatomy:** data-grid table with columns: Shared With, Metric, Aggregation, Expiration, Status, Revoke action

**States:** Active row (full opacity) · Inactive row (0.5 opacity) · Revoking

**Status column:** ACTIVE (green bold) · DEACTIVATED (muted, smaller). Formerly showed api_token_hash — changed for security.

**Revoke:** hx-delete per relationship. HX-Refresh triggers full page reload to ensure consistency.

**Do:** Show grantee handle prominently · Indicate active vs revoked · Provide individual revoke

**Don't:** Show API tokens or hashes · Omit expiration info · Allow revoke of already-inactive relationships
