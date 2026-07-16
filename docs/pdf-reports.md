# PDF Report Generation

## Overview
Erstelle konfigurierbare PDF-Berichte für Arztbesuche, eigenes Tracking oder zum Teilen.
Nutzer wählt Zeitraum und welche Sektionen enthalten sein sollen.

## Design

### Report Template System

```
ReportTemplate
├── title: str ("Gesundheitsbericht Q1 2026")
├── date_range: (start, end)
├── sections: [Section...]
└── branding: { logo?, color_scheme }

Section
├── type: enum
│   ├── summary          — Text-Zusammenfassung (AI-generiert)
│   ├── metrics_table    — Tabelle mit Metriken + Trends
│   ├── metrics_chart    — Liniendiagramm (SVG → PDF)
│   ├── lab_results      — Labortabelle mit Referenzbereichen
│   ├── goal_progress    — Ziel-Fortschritt
│   ├── body_measurements — Körpermaß-Tabelle
│   ├── workout_summary  — Workout-Statistiken
│   ├── mood_summary     — Stimmungs-Verlauf
│   └── custom_text      — Freitext/Markdown
├── config: json (metrisch-spezifische Konfiguration)
└── order: int
```

### Report
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| title | str | |
| template_json | json | Vollständige Template-Definition |
| generated_at | datetime | |
| file_path | str | Pfad zum PDF |
| file_size_bytes | int | |
| expires_at | datetime? | Auto-delete |

## Report Sections (Detail)

### Summary (AI-generated)
- Nutzt existierende Insight-Infrastruktur (LLM-Provider)
- Prompt: "Erstelle eine Zusammenfassung der Gesundheitsdaten für [Zeitraum]..."
- Auf Deutsch/Englisch je nach User-Locale

### Metrics Table
- Pro MetricType: Aktueller Wert, Durchschnitt, Min/Max, Trend-Pfeil
- Statistische Tests: Signifikanz der Veränderung (Mann-Kendall)

### Metrics Chart
- SVG-Charts via matplotlib/plotly serverseitig, in PDF eingebettet
- Oder: Client-seitiges Chart → PNG → PDF-Konvertierung

### Lab Results
- Marker, Wert, Einheit, Referenzbereich, Abweichung farblich (grün/gelb/rot)
- Trend-Pfeil zum vorherigen Wert

### Goal Progress
- Ziel, Zielwert, Aktueller Wert, Fortschrittsbalken, Status

## Generierung

Backend (Python):
- **WeasyPrint** oder **ReportLab** für PDF-Generierung
- Charts: `matplotlib` (serverseitig) als SVG/PNG → in PDF embedden
- Alternativ: HTML → PDF mit WeasyPrint (einfachere Styling mit CSS)

Frontend:
- **Vorschau** vor Generierung (HTML-Rendering im Browser)
- "Download PDF" / "Teilen" Buttons

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/reports/preview | Preview (returns HTML) |
| POST | /api/v1/reports/generate | Generate PDF |
| GET | /api/v1/reports | List past reports |
| GET | /api/v1/reports/{id} | Get report metadata |
| GET | /api/v1/reports/{id}/download | Download PDF |
| DELETE | /api/v1/reports/{id} | Delete |
| POST | /api/v1/reports/templates | Save template |
| GET | /api/v1/reports/templates | List templates |
| DELETE | /api/v1/reports/templates/{id} | Delete template |

## Frontend

- **ReportBuilder** — Drag-and-Drop Sektions-Builder
- **ReportPreview** — HTML-Vorschau (wie gedruckt)
- **ReportHistory** — Liste vergangener Reports
- **SectionConfigurator** — Pro Sektion: Metriken auswählen, Zeitraum, Chart-Typ

## Integration Points
- **Insights/AI** → Summary-Sektion
- **Lab Results** → Labor-Sektion
- **Body Measurements** → Körpermaß-Sektion
- **Workouts** → Workout-Statistik-Sektion
- **Goals** → Ziel-Fortschritt-Sektion
- **Analytics** → Trend-Daten
- **Export** → Könnte bestehenden CSV/JSON-Export ergänzen oder ersetzen

## Open Questions
- PDF-Bibliothek: WeasyPrint (HTML→PDF, einfach) vs. ReportLab (mehr Kontrolle, komplexer)?
- Soll der Bericht client-seitig (jsPDF) oder server-seitig generiert werden?
- Client-seitig: Offline-fähig. Server-seitig: Bessere Performance bei großen Daten.
- Templates: Speichern wir Templates als User-Daten (sync-bar) oder nur lokal?
- DSGVO-konform? PDFs enthalten Gesundheitsdaten → verschlüsselt speichern?
- Soll der Report per E-Mail versendet werden können? (SMTP-Integration)

## Ergänzungen von Philipp
PDF-Bibliothek: Das überlasse ich dir, die Frage ist dann natürlich auch, ob wir die PDFs auch lokal oder nur Serverseitig generieren lassen wollen.. Ich tendiere ja mitunter zu beidem.
Keine Ahnung was du mit Templates meinst..
DSGVO Konformität ist wichtig
Nein, bis jetzt soll der Report nicht automatisch per email versendet werden, das kann der User erstmal selber machen