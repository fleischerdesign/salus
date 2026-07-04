# Forms — Validation, Error Handling & Patterns

**Form submission:** HTMX-driven (`hx-post`/`hx-put`) with standard `action`/`method` fallback for non-JS.

**Validation:** Server-side validated. Errors returned as HTML response with alert + field-level error spans.

**Field-level errors:**
- Error span below input, color: `{colors.error-700}`
- Input border: `{colors.error-400}`
- `aria-describedby` links input to error span ID
- Error spans use `role="alert"` for immediate announcement

**Required fields:**
- Asterisk after label text (*)
- HTML `required` attribute on input
- Server-side validation even with HTML5 validation

**Form layout patterns:**
- `.form-stack` — vertical input stack (default), 16px gap
- `.form-row` — side-by-side inputs, 16px gap (max 3 fields)
- `.form-actions` — submit + cancel bar, 16px gap, 8px top margin

**Progressive enhancement:**
- `<form>` must have both `hx-*` attributes AND `action` + `method`
- JS disabled: form submits normally (full page reload)
- JS enabled: HTMX intercepts, partial update

**Do:** Always include action/method fallback · Use aria-describedby for errors · Mark required fields · Validate server-side

**Don't:** Rely solely on HTML5 validation · Use color alone for errors · Forget error association
