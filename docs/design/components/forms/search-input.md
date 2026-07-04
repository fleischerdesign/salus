# Search Input

> Status: **Design spec only — not yet implemented.**

**Anatomy:** Search icon (left) + Input field + Clear button (appears when text present, X icon) + Optional filter dropdown

**States:** Empty · Typing (clear button visible) · Searching (spinner replaces search icon) · Results · No results

**Debounce:** 300ms before triggering search. Results load via HTMX.

**Clear button:** 20px X icon, slate-400, absolute positioned right. Click clears input and resets results.

**Do:** Use for filtering/searching data · Debounce input · Show clear button · Show "No results" when empty

**Don't:** Search on every keystroke (use debounce) · Hide clear button · Use placeholder as only label
