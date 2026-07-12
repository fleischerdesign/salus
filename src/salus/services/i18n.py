PLUGIN_TRANSLATIONS: dict[str, dict[str, str]] = {}


def register_plugin_translations(translations: dict[str, dict[str, str]]) -> None:
    for lang, mapping in translations.items():
        if lang not in PLUGIN_TRANSLATIONS:
            PLUGIN_TRANSLATIONS[lang] = {}
        PLUGIN_TRANSLATIONS[lang].update(mapping)


def translate(text: str, locale: str = "en") -> str:
    return PLUGIN_TRANSLATIONS.get(locale, {}).get(text, text)
