def test_translate_function():
    from salus.services.i18n import translate
    assert translate("fulfilled", "de") == "Erreicht"
    assert translate("partial", "de") == "Teilweise"
    assert translate("pending", "de") == "Ausstehend"
    assert translate("non-existent-key", "de") == "non-existent-key"
