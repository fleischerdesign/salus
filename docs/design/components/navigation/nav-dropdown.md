# Nav Dropdown

**Tokens:** `--nav-dropdown-bg`, `--nav-dropdown-border`, `--nav-dropdown-shadow`, `--nav-dropdown-radius`

**Anatomy:** Trigger link (label-md, with arrow icon) + Dropdown panel

**States:** Closed · Open (on hover, lg shadow, 8px radius, arrow rotates 180deg)

**Contents:** Link list (label-md, full-width, hover: slate-50 bg). Active link: primary text.

**Interaction:** CSS :hover reveal with ::before bridge element (prevents hover-gap flicker). Sub-second delay on mouseleave.

**Do:** Use for grouped navigation · Keep dropdown width auto-fit · Limit to 2 levels

**Don't:** Nest dropdowns deeper than 2 levels · Omit hover bridge · Make items too long (>25 chars)
