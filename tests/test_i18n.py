def test_translate_function():
    from salus.services.i18n import translate
    assert translate("fulfilled", "de") == "fulfilled"
    assert translate("non-existent-key", "de") == "non-existent-key"


def test_plugin_translations():
    from salus.services.i18n import register_plugin_translations, translate
    register_plugin_translations({"de": {"Demo Summary": "Demo-Zusammenfassung"}})
    assert translate("Demo Summary", "de") == "Demo-Zusammenfassung"
