# Salus 2.0 — Die 5 Lückenlosen User Journey Flows
**Dokument:** `05-user-journey-flows.md`  
**Status:** Verbindlich

---

## Übersicht der 5 Kern-Abläufe

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 DIE 5 SALUS TAGES-FLOWS                │
                  └────────────────────────────────────────────────────────┘
                                               │
    ┌──────────────────────┬───────────────────┼───────────────────┬──────────────────────┐
    ▼                      ▼                   ▼                   ▼                      ▼
1. MORGEN-ROUTINE      2. KRAFTTRAINING    3. MITTAG & ERNÄHR. 4. ABEND-REFLEXION     5. ARZT-EXPORT
• Schlaf-Hypnogramm    • Split vorschlagen • 1-Tap Wasser-Welle• Koffein-Cutoff       • 90-Tage Filter
• 1-Tap Schlaf-Rating  • Große Touch-Pads  • Fasten-Abschluss  • 2D-Stimmungs-Kugel   • Asymmetrischer
• Zirkadianes Licht    • Auto Rest-Timer   • Barcode / Rezept  • Journal-Leitfragen     E2EE Link / PIN
• Morgen-Habit-Swipe   • 1RM-Rekord Funken • Makro-Donut Update• Melatonin-Dimmung    • PDF-Klinikreport
```

---

## 1. Flow 1: Die Morgen-Routine (*Morning Awakening & Readiness*)

1. **Einstieg:** Der Nutzer öffnet die App oder tippt auf das Morgen-Widget.
2. **Hero-Begrüßung:** Kontextuelle Begrüßung (*"Guten Morgen, Philipp"*) + visuelle Darstellung des Schlaf-Hypnogramms der vergangenen Nacht.
3. **1-Tap Schlaf-Check-in:** Bewertung des subjektiven Erholungsgefühls (1–5 Sterne).
4. **Readiness-Status:** Sofortige Synthese: *"Erholung: 92% • Optimaler Tag für intensives Training"*.
5. **Zirkadianer Hinweis:** *"☀️ Ideales Sonnenlicht-Fenster: Nutze die nächsten 45 Minuten für natürliches Tageslicht zur Cortisol-Aktivierung"*.
6. **Morgen-Habits:** Schnelle Wischgeste über Morgen-Gewohnheiten (z. B. *"Großes Glas Wasser"*, *"5 Min Dehnen"*).
7. **Fasten-Restzeit:** Kurzer Blick auf den Fasten-Ring (*"Noch 2h 15m bis zum Essensfenster"*).
- **Ziel:** Der gesamte Morgen-Check-in dauert **unter 20 Sekunden**.

---

## 2. Flow 2: Das Krafttraining (*Live Active Session Mode*)

1. **Start:** Tipp auf `Workout starten` im Dashboard oder Quick-Log Hub.
2. **Split-Vorschlag:** Salus schlägt automatisch den nächsten Split im Plan vor (z. B. *"Push Day A"*).
3. **Live Active Screen:**
   - **Sticky Top Bar:** Gesamtzeit, Tonnage-Volumen, Satz-Zähler.
   - **Übungs-Karte:**
     - Zeigt das vorherige Gewicht/Wiederholungen der letzten Woche als Referenz (*"Letztes Mal: 80kg × 10"*).
     - **Große Touch-Ziffernfelder:** Schnelle Anpassung von Gewicht und Wiederholungen.
     - **Satz-Häkchen `[ ✓ ]`:** Satz als beendet markieren.
4. **Automatischer Pausen-Timer:** Ein schwebender Kreisbalken zählt sofort die 90s Pause herunter (Vibration/Signalton bei 0s).
5. **PR-Celebration:** Bei Überbieten des 1RM-Rekords erscheint ein subtiler Vektor-Lichtburst mit Trophäen-Hinweis.
6. **Abschluss:** Klick auf `Workout beenden` öffnet eine feierliche Summary-Karte mit bewegtem Gesamtvolumen, Rekorden und der aktualisierten `MuscleHeatmap2D`.

---

## 3. Flow 3: Mittag & Ernährung (*Midday Fuel & Hydration*)

1. **Hydration:** Tipp auf `+500ml` im Wasserglas-Widget → Welle steigt flüssig an.
2. **Fasten-Abschluss:** Fastenzeit von 16h ist vollendet → Feierliche Animation *"Fastenziel erreicht"* → Tipp auf `Fasten beenden`.
3. **Mahlzeit erfassen:**
   - Barcode scannen (Kamera) oder Schnellsuche nach Zutat/Rezept.
   - Portionsgröße wählen → Speichern.
4. **Live-Feedback:** Der `MacroDonutGauge` auf dem Dashboard aktualisiert sich nahtlos; der Proteinbalken wächst.

---

## 4. Flow 4: Abend-Reflexion & Wind-Down (*Evening Wind-down*)

1. **14:30 Uhr:** Zirkadianer Koffein-Cutoff Hinweis (*"Letzte Tasse Kaffee für ungestörten Tiefschlaf"*).
2. **20:30 Uhr:** Abendlicher Reflexions-Impuls:
   - Stimmung auf der 2D-Valenz-Kugel antippen.
   - 1–2 Sätze im Journal notieren (Optionale geführte Prompts).
3. **21:30 Uhr:** Melatonin-Synthese-Phase:
   - Salus schaltet sanft in gedimmte Kontraste zur Blaulicht-Reduzierung.
   - Schlaf-Coach zeigt die ideale Zubettgeh-Zeit an (z. B. 22:45 Uhr).

---

## 5. Flow 5: Klinischer Arzt-Export (*Consultation & E2EE Sharing*)

1. **Navigation:** `/settings/shares` oder Klick auf `Bericht exportieren` in den Laboren/Vitalwerten.
2. **Filterung:** Zeitraum wählen (*"Letzte 90 Tage"*) + Häkchen für gewünschte Datenpunkte (*Blutdruck, Großes Blutbild, Medikamente*).
3. **Ausgabe:**
   - **Option A:** Passwortgeschützter, asymmetrisch verschlüsselter E2EE-Link mit PIN für den Arzt.
   - **Option B:** Hochauflösender, druckfertiger klinischer PDF-Bericht mit farbigen Referenz-Tachos und Verlaufs-Diagrammen.
