TRANSLATIONS = {
    "de": {
        # Navigation & Sidebar
        "Dashboard": "Dashboard",
        "Metrics": "Metriken",
        "Entries": "Einträge",
        "Goals": "Ziele",
        "Settings": "Einstellungen",
        "Admin": "Admin",
        "Logout": "Abmelden",
        "Login": "Anmelden",
        "Register": "Registrieren",

        # Dashboard / Welcome
        "Welcome to Salus": "Willkommen bei Salus",
        "Health data tracker": "Gesundheitsdaten-Tracker",
        "Dismiss Onboarding": "Onboarding ausblenden",
        "Health Connect Integration": "Health Connect Integration",
        "Copy Token": "Token kopieren",
        "No metrics enabled yet. Go to Settings or Metrics to enable widgets.": "Noch keine Metriken aktiviert. Gehe zu den Einstellungen oder Metriken, um Widgets zu aktivieren.",

        # General Actions
        "Save": "Speichern",
        "Cancel": "Abbrechen",
        "Delete": "Löschen",
        "Add Entry": "Eintrag hinzufügen",
        "Create Goal": "Ziel erstellen",
        "Edit": "Bearbeiten",
        "Back": "Zurück",

        # Metrics Page
        "Metric Types": "Metriktypen",
        "System Metrics": "Systemmetriken",
        "Custom Metrics": "Eigene Metriken",
        "Name": "Name",
        "Unit": "Einheit",
        "Data Type": "Datentyp",
        "Color": "Farbe",
        "Actions": "Aktionen",
        "Create Custom Metric": "Eigene Metrik erstellen",

        # Goals Page
        "Your Goals": "Deine Ziele",
        "Target Value": "Zielwert",
        "Direction": "Richtung",
        "Frequency": "Häufigkeit",
        "Deadline": "Frist",
        "Status": "Status",
        "Active": "Aktiv",
        "Completed": "Abgeschlossen",
        "Create New Goal": "Neues Ziel erstellen",

        # Settings Page
        "Account Settings": "Kontoeinstellungen",
        "Language": "Sprache",
        "Theme": "Design",
        "Dark": "Dunkel",
        "Light": "Hell",
        "API Tokens": "API-Token",
        "Generate Token": "Token generieren",
        "Connected Sources": "Verbundene Quellen",
        "Change Password": "Passwort ändern",
        "Export Data": "Daten exportieren",
        "Import Data": "Daten importieren",
    }
}


def translate(text: str, locale: str = "en") -> str:
    if locale == "en":
        return text
    return TRANSLATIONS.get(locale, {}).get(text, text)
