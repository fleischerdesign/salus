from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from jinja2 import BaseLoader

if TYPE_CHECKING:
    from jinja2 import Environment

MACRO_RE = re.compile(r"{%\s*macro\s+(\w+)\s*\(")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _build_macro_index() -> str:
    lines: list[str] = []
    for macro_path in sorted(TEMPLATES_DIR.rglob("macro.html")):
        rel = str(macro_path.relative_to(TEMPLATES_DIR))
        content = macro_path.read_text(encoding="utf-8")
        names = MACRO_RE.findall(content)
        if names:
            lines.append(f'{{%- from "{rel}" import {", ".join(names)} -%}}')
    return "\n".join(lines) + "\n"


_MACRO_IMPORTS: str | None = None


def get_macro_imports() -> str:
    global _MACRO_IMPORTS
    if _MACRO_IMPORTS is None:
        _MACRO_IMPORTS = _build_macro_index()
    return _MACRO_IMPORTS


class AutoImportLoader(BaseLoader):
    def __init__(self, delegate: BaseLoader) -> None:
        self._delegate = delegate

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str | None, Callable[[], bool] | None]:
        source, filename, uptodate = self._delegate.get_source(environment, template)
        if "/macro.html" not in str(filename):
            source = get_macro_imports() + source
        return source, filename, uptodate

    def list_templates(self) -> list[str]:
        return self._delegate.list_templates()


def render_attrs(attrs: dict, exclude: str | list[str] | None = None) -> str:
    """Convert Python keyword arguments into HTML/HTMX attributes.

    Translates underscores to dashes (e.g. hx_post -> hx-post) and strips
    trailing underscores (e.g. class_ -> class). Boolean True values are
    rendered as bare attributes (e.g. disabled=True -> disabled).

    The optional 'exclude' parameter specifies attributes to ignore (e.g. ['class']).
    """
    from markupsafe import Markup

    exclude_set = set()
    if exclude:
        if isinstance(exclude, str):
            exclude_set.add(exclude)
        else:
            exclude_set.update(exclude)

    parts: list[str] = []
    for k, v in attrs.items():
        if k in exclude_set or v is None or v is False:
            continue

        # Normalize key: replace underscores with dashes, strip trailing underscores
        # Example: hx_post -> hx-post, class_ -> class, class -> class
        key = k.rstrip("_").replace("_", "-")
        if key == "hyperscript":
            key = "_"

        if v is True:
            parts.append(key)
        else:
            # Escape quotes in the value
            escaped_val = str(v).replace('"', "&quot;")
            parts.append(f'{key}="{escaped_val}"')

    return Markup(" " + " ".join(parts)) if parts else ""
# Trigger reload to re-index new macros - V3

