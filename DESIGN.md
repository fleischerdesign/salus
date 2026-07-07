# Salus Design System

Salus uses a modern, light-weight, and highly-maintainable Design System. The styling is built entirely with **Vanilla CSS Custom Properties (CSS variables)**, **Jinja2 component macros**, and **HTMX**, with no external framework dependencies (no TailwindCSS/Bootstrap).

The design style follows a **Modern Corporate + Minimalism** aesthetic — authoritative yet empathetic, tailored for health administrators and individuals seeking clean data visibility.

---

## 1. CSS Architecture & Tokens

The Design System operates on a native three-layer token cascade:

$$\text{Global Tokens (Raw Values)} \longrightarrow \text{Semantic Tokens (Meaning)} \longrightarrow \text{Component Styles}$$

### 1.1 Single Source of Truth: `tokens.css`
All global design tokens (colors, typography scales, spacings, shadows, durations, and transitions) are defined directly in [src/salus/static/tokens.css](file:///home/philipp/dev/salus/src/salus/static/tokens.css).

*   **Light Theme (Default):** Defined under the `:root` and `[data-theme="light"]` selectors.
*   **Dark Theme:** Overridden under the `[data-theme="dark"]` selector and the `@media (prefers-color-scheme: dark)` media query for native system theme detection.

This native CSS architecture guarantees:
*   **No Build Steps:** Instant Hot-Reloading in the browser.
*   **IDE Autocomplete:** IDEs natively index the variables, providing autocompletion and visual color pickers.
*   **Barrierefreiheit:** Color contrasts are explicitly declared for both light and dark modes to satisfy accessibility requirements.

### 1.2 BEM Naming Conventions
All component-specific CSS classes use the **BEM (Block-Element-Modifier)** standard:
*   `Block`: `.btn`, `.card`, `.input` (the wrapper element)
*   `Element`: `.btn__icon`, `.input__field` (descendants prefixed by `__`)
*   `Modifier`: `.btn--danger`, `.btn--small` (variants prefixed by `--` or using custom `data-*` attributes)

---

## 2. Component Development & Colocation

UI components are stored under [src/salus/templates/components/ui/](file:///home/philipp/dev/salus/src/salus/templates/components/ui/) following the **Colocation Pattern**:

```
templates/components/ui/btn/
├── macro.html  ← Jinja2 macro definition
└── style.css   ← Component-specific styles
```

### 2.1 CSS Bündelung (Auto-Build)
Individual `style.css` files are concatenated into [src/salus/static/components.css](file:///home/philipp/dev/salus/src/salus/static/components.css). 
*   **Automatisierung:** This build process happens **automatically on application startup** (within the lifespan configuration of FastAPI). No manual terminal commands are needed.

### 2.2 Dynamic Attribute Forwarding (Jinja2 + HTMX)
Jinja2 macros do not declare explicit parameters for HTML, HTMX, or Hyperscript events. Instead, they use the custom `render_attrs` filter to dynamically forward arbitrary attributes:

```jinja2
{% macro btn(label=none, variant="primary") %}
  <button class="btn" data-variant="{{ variant }}" {{ kwargs | render_attrs }}>
    {% if label %}<span class="btn__label">{{ label }}</span>{% endif %}
  </button>
{% endmacro %}
```

In your page templates, you can use any HTMX attributes seamlessly:
```jinja2
{{ btn("Save", hx_post="/goals", hx_target="#grid", hx_swap="outerHTML") }}
```

---

## 3. The Living Styleguide (Dokumentation)

Instead of maintaining separate Markdown specification files (which quickly fall out of sync with code), Salus uses a **Living Styleguide**:

*   **URL:** `/design-system` (rendered via [src/salus/templates/pages/design_system.html](file:///home/philipp/dev/salus/src/salus/templates/pages/design_system.html))
*   **Single Source of Truth:** Every component variant, state (disabled, loading), and interactive behavior is rendered live using the actual Jinja2 macros.
*   **Validation:** If a component renders correctly on the `/design-system` page and reacts to the theme toggle, its styling is officially validated.

---

## 4. Guidelines for Adding a New Component

1.  **Check Tokens:** Open [tokens.css](file:///home/philipp/dev/salus/src/salus/static/tokens.css) to check if your desired typography, space, or color scales already exist.
2.  **Create Directory:** Add a folder under `templates/components/ui/<component_name>/`.
3.  **Define Macro (`macro.html`):** Keep parameters minimal (only component options). Use `{{ kwargs | render_attrs }}` on the wrapper tag.
4.  **Write Styles (`style.css`):** Write local BEM classes, using the CSS variables from `tokens.css`.
5.  **Restart Server:** The styling will compile automatically.
6.  **Add to Styleguide:** Register the new component in [design_system.html](file:///home/philipp/dev/salus/src/salus/templates/pages/design_system.html) to document its usage.
