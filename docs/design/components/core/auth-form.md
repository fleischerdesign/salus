# Auth Form

**Anatomy:** Centered card (max 440px, 32px padding, rounded-lg) + Title (headline-lg) + Subtitle (body-md, muted) + Form fields + Submit button + Divider "or" + Provider buttons

**States:** Default · Submitting (button shows spinner) · Error (alert above form)

**Provider buttons:** Full-width, 12px padding, slate-200 border, rounded-md. Hover: slate-50 bg. Icons: 20px Material Symbols.

**Divider:** Horizontal line with "or" label-sm in center. 24px vertical margin.

**Responsive:** Padding reduces to 24px 16px below 600px.

**Do:** Center on page · Show provider buttons for OIDC/LDAP · Keep form concise · Show error alert for failures

**Don't:** Overwhelm with too many providers · Forget password reset link · Show raw error messages
