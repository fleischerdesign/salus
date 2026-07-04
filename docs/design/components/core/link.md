# Link

**Anatomy:** Inline text with optional icon

**States:** Default (inherit color, no underline) · Hover (color changes, no underline by default) · Focus (outline/ring for accessibility) · Visited · Active · External (with external-link icon)

**Variants:**
- Navigation link: label-md, slate-600 → primary on hover, 2px primary border-bottom when active
- Inline text link: body-md, primary color, underline on hover, in running text
- Action link: like button-ghost but inline, for "Edit", "View all", "Learn more"

**Accessibility:** Focus visible ring. Distinguishable from regular text by color (NOT by color alone — also font-weight or underline on hover). External links: `rel="noopener noreferrer"`.

**Do:** Use primary color for clickable links · Show underline on hover · Distinguish from body text · Add external icon for off-site links

**Don't:** Use color alone to indicate link · Make link text generic ("click here") · Omit focus styles
