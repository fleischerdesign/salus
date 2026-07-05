from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from jinja2 import BaseLoader

if TYPE_CHECKING:
    from jinja2 import Environment

MACRO_RE = re.compile(r'{%\s*macro\s+(\w+)\s*\(')

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
COMPONENTS_DIR = TEMPLATES_DIR / "components" / "ui"


def _build_macro_index() -> str:
    lines: list[str] = []
    for macro_path in sorted(COMPONENTS_DIR.glob("*/macro.html")):
        rel = str(macro_path.relative_to(TEMPLATES_DIR))
        content = macro_path.read_text(encoding="utf-8")
        names = MACRO_RE.findall(content)
        if names:
            lines.append(
                f'{{%- from "{rel}" import {", ".join(names)} -%}}'
            )
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
        if "components/ui/" not in str(filename):
            source = get_macro_imports() + source
        return source, filename, uptodate

    def list_templates(self) -> list[str]:
        return self._delegate.list_templates()
