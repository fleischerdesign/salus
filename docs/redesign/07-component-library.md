# Salus 2.0 — Komponenten-Bibliothek (Atomic Design Specs)
**Dokument:** `07-component-library.md`  
**Status:** Verbindlich

---

## 1. Vollständiges Komponenten-Inventar nach Kategorien (86 Spezifikationen)

### 1.1 Atome & Basis-UI-Primitives (Atoms)
| Komponente | Datei / Detail-Spezifikation | Zweck |
|---|---|---|
| **`Btn.svelte`** | [**`components/15-Btn.md`**](./components/15-Btn.md) | Universal-Button (Primary, Secondary, Ghost, Danger, Vital, Pill) |
| **`Input.svelte`** | [**`components/16-Input.md`**](./components/16-Input.md) | Texteingabe & Ziffernfeld mit Floating Label & Numeric Keypad Mode |
| **`SearchInput.svelte`** | [**`components/81-SearchInput.md`**](./components/81-SearchInput.md) | Dediziertes Suchfeld mit Debounce, Clear-Button & Shortcut-Hint |
| **`PasswordInput.svelte`** | [**`components/82-PasswordInput.md`**](./components/82-PasswordInput.md) | Passwortfeld mit Auge-Toggle & dynamischem Stärkebalken |
| **`Textarea.svelte`** | [**`components/63-Textarea.md`**](./components/63-Textarea.md) | Auto-resizing mehrzeiliges Textfeld mit Zeichenzähler & Markdown |
| **`Badge.svelte`** | [**`components/47-Badge.md`**](./components/47-Badge.md) | Status- & Kategorie-Pille mit Live-Dot, Counter & Farbvarianten |
| **`ToggleSwitch.svelte`** | [**`components/48-ToggleSwitch.md`**](./components/48-ToggleSwitch.md) | Taktiler iOS/macOS-Style Schalter mit Haptik & Daumen-Physik |
| **`Checkbox.svelte`** | [**`components/51-Checkbox.md`**](./components/51-Checkbox.md) | Animierte Checkbox mit SVG-Draw-in & Indeterminate-Status |
| **`Slider.svelte`** | [**`components/49-Slider.md`**](./components/49-Slider.md) | Feinfühliger Bereichs-Schieberegler mit Werte-Blase & Ticks |
| **`SegmentedControl.svelte`** | [**`components/17-SegmentedControl.md`**](./components/17-SegmentedControl.md) | Schiebende Pillen-Auswahl mit federnder CSS-Animation |
| **`ProgressBar.svelte`** | [**`components/66-ProgressBar.md`**](./components/66-ProgressBar.md) | Linearer Fortschrittsbalken mit Determinate-/Indeterminate-Modus |
| **`Spinner.svelte`** | [**`components/67-Spinner.md`**](./components/67-Spinner.md) | Minimalistischer SVG-Ladekreis mit weichem Nachlauf |
| **`Kbd.svelte`** | [**`components/69-Kbd.md`**](./components/69-Kbd.md) | 3D-Tastaturkappe für Shortcuts (`[ ⌘K ]`, `[ Esc ]`, `[ L ]`) |
| **`Avatar.svelte`** | [**`components/58-Avatar.md`**](./components/58-Avatar.md) | Benutzer-Avatar mit Initialen-Gradient & Live-Sync Status-Dot |
| **`Divider.svelte`** | [**`components/59-Divider.md`**](./components/59-Divider.md) | 1px-Haarlinie mit optionalem zentriertem Label oder Icon |
| **`Tooltip.svelte`** | [**`components/55-Tooltip.md`**](./components/55-Tooltip.md) | Glasmorphismus-Mikro-Tooltip mit Rand-Kollisionserkennung |
| **`ColorPicker.svelte`** | [**`components/72-ColorPicker.md`**](./components/72-ColorPicker.md) | Harmonische OKLCH-Farbfeldauswahl für Metriken & Habits |
| **`RatingPicker.svelte`** | [**`components/73-RatingPicker.md`**](./components/73-RatingPicker.md) | 1–5 Sterne- & Batterie-Wähler für Schlafqualität & Erholung |
| **`AudioCue.svelte`** | [**`components/77-AudioCue.md`**](./components/77-AudioCue.md) | Web Audio API synthetisierte Töne (Timer-Gong, PR-Fanfare) |
| **`AspectRatio.svelte`** | [**`components/83-AspectRatio.md`**](./components/83-AspectRatio.md) | Geometrischer Container für feste Seitenverhältnisse (16:9, 1:1)|
| **`Collapsible.svelte`** | [**`components/84-Collapsible.md`**](./components/84-Collapsible.md) | Low-Level CSS-Grid Höhen-Aufklapp-Primitiv (Zero Jank) |
| **`ScrollArea.svelte`** | [**`components/85-ScrollArea.md`**](./components/85-ScrollArea.md) | Maßgeschneiderter Scroll-Bereich mit weichen Ausblend-Masken |
| **`MethodologyBadge.svelte`** | [**`components/27-MethodologyBadge.md`**](./components/27-MethodologyBadge.md) | Wissenschaftliches Transparenz-Popover mit Formel, p-Wert & n |
| **`DataQualityFlagBadge.svelte`**| [**`components/45-DataQualityFlagBadge.md`**](./components/45-DataQualityFlagBadge.md)| Plausibilitäts-Warnung bei Ausreißern mit 1-Klick Reparatur |
| **`NutritionBudgetBar.svelte`** | [**`components/37-NutritionBudgetBar.md`**](./components/37-NutritionBudgetBar.md) | Kompakte Makro-Fortschrittsleiste für Dashboard-Kacheln |

### 1.2 Moleküle & Interaktive UI-Einheiten (Molecules)
| Komponente | Datei / Detail-Spezifikation | Zweck |
|---|---|---|
| **`SurfaceCard.svelte`** | [**`components/21-SurfaceCard.md`**](./components/21-SurfaceCard.md) | Modulare Basiskarte mit OKLCH-Elevationen, Hover-Lift & Drag-Handle |
| **`MetricTile.svelte`** | [**`components/02-MetricTile.md`**](./components/02-MetricTile.md) | Modulare Kachel mit Sparkline, Delta-Badge & Ziel-Balken (S/M/L) |
| **`SelectDropdown.svelte`** | [**`components/50-SelectDropdown.md`**](./components/50-SelectDropdown.md) | Durchsuchbares Auswahl-Dropdown mit Icons, Gruppen & Filter |
| **`RadioGroup.svelte`** | [**`components/52-RadioGroup.md`**](./components/52-RadioGroup.md) | Elegante Radio-Kacheln für exklusive Optionen (z.B. Fasten-Pläne)|
| **`DatePicker.svelte`** | [**`components/64-DatePicker.md`**](./components/64-DatePicker.md) | Barrierefreier Kalender-Wähler für Einzeldaten & Zeiträume |
| **`TimePicker.svelte`** | [**`components/65-TimePicker.md`**](./components/65-TimePicker.md) | Präzisions-24h-Uhrzeitwähler mit Schnellwahl-Presets |
| **`TagInput.svelte`** | [**`components/70-TagInput.md`**](./components/70-TagInput.md) | Multi-Tag & Chip-Eingabefeld mit Autovervollständigung |
| **`SwipeableRow.svelte`** | [**`components/71-SwipeableRow.md`**](./components/71-SwipeableRow.md) | Touch-Wischzeile für Mobile (Swipe-to-Complete / Swipe-to-Delete) |
| **`Popover.svelte`** | [**`components/56-Popover.md`**](./components/56-Popover.md) | Anker-positioniertes schwebendes Panel mit Click-Outside-Erkennung|
| **`DropdownMenu.svelte`** | [**`components/57-DropdownMenu.md`**](./components/57-DropdownMenu.md) | Kontext-Aktionsmenü (Edit, Size, Delete) mit Tastatur-Steuerung |
| **`ContextMenu.svelte`** | [**`components/86-ContextMenu.md`**](./components/86-ContextMenu.md) | Desktop Rechtsklick-Kontextmenü für sofortige Aktionen |
| **`Accordion.svelte`** | [**`components/60-Accordion.md`**](./components/60-Accordion.md) | Sanft aufklappbare Bereiche mit rotierendem SVG-Chevron |
| **`Tabs.svelte`** | [**`components/61-Tabs.md`**](./components/61-Tabs.md) | Horizontale Tab-Leiste mit schiebender Pillen-Auswahl |
| **`Pagination.svelte`** | [**`components/78-Pagination.md`**](./components/78-Pagination.md) | Barrierefreie Seitennummerierung mit Zeilen-pro-Seite Wähler |
| **`Stepper.svelte`** | [**`components/79-Stepper.md`**](./components/79-Stepper.md) | Mehrstufiger Wizard-Fortschritt mit Aktiv- & Erledigt-Status |
| **`OtpInput.svelte`** | [**`components/80-OtpInput.md`**](./components/80-OtpInput.md) | 4–6-stelliger PIN- & OTP-Eingabeblock für E2EE & 2FA |
| **`Breadcrumbs.svelte`** | [**`components/62-Breadcrumbs.md`**](./components/62-Breadcrumbs.md) | Hierarchischer Orientierungspfad für Unter- und Detailseiten |
| **`HabitCheckCircle.svelte`** | [**`components/18-HabitCheckCircle.md`**](./components/18-HabitCheckCircle.md) | Taktiler Toggle mit Lottie-/SVG-Completion-Burst & Streak-Badge |
| **`ClinicalGaugeMeter.svelte`** | [**`components/06-ClinicalGaugeMeter.md`**](./components/06-ClinicalGaugeMeter.md) | 4-Zonen-Tachometer mit Präzisions-Nadel & Referenzbereich |
| **`LabPanelCard.svelte`** | [**`components/35-LabPanelCard.md`**](./components/35-LabPanelCard.md) | Labor-Panel-Kachel (z.B. Lipidprofil, Blutbild) mit Statuspille |
| **`RestTimer.svelte`** | [**`components/19-RestTimer.md`**](./components/19-RestTimer.md) | Schwebender Countdown-Balken für Trainingspausen mit +30s & Signal |
| **`WorkoutSplitCard.svelte`** | [**`components/39-WorkoutSplitCard.md`**](./components/39-WorkoutSplitCard.md) | Trainingsplan-Split-Kachel mit Muskel-Chips & Schnellstart |
| **`MealItemRow.svelte`** | [**`components/29-MealItemRow.md`**](./components/29-MealItemRow.md) | Mahlzeiten-Eintragszeile mit Portionsanpassung & Makro-Live-Werten |
| **`MedicationDoseCard.svelte`**| [**`components/30-MedicationDoseCard.md`**](./components/30-MedicationDoseCard.md)| Medikamenten-Einnahmekarte mit 1-Tap Adhärenz & Vorrats-Warnung |
| **`E2EEShareCard.svelte`** | [**`components/41-E2EEShareCard.md`**](./components/41-E2EEShareCard.md) | Kryptographische Arzt-Freigabekarte mit PIN & Countdown |
| **`LeaderboardRow.svelte`** | [**`components/42-LeaderboardRow.md`**](./components/42-LeaderboardRow.md) | Anonymisierte Community-Ranglisten-Zeile für Challenges |
| **`AchievementCard.svelte`** | [**`components/43-AchievementCard.md`**](./components/43-AchievementCard.md) | 3D-Tilt Trophäen-Karte mit Rangstufe & Fortschrittsbalken |
| **`WidgetGalleryCard.svelte`** | [**`components/20-WidgetGalleryCard.md`**](./components/20-WidgetGalleryCard.md) | Miniaturisierte animierte Live-Vorschau für den Add-Widget Katalog |
| **`SkeletonCard.svelte`** | [**`components/22-SkeletonCard.md`**](./components/22-SkeletonCard.md) | Shimmer-Ladeplatzhalter in exakter Ziel-Kacheldimension (Zero CLS) |
| **`EmptyState.svelte`** | [**`components/23-EmptyState.md`**](./components/23-EmptyState.md) | Ästhetischer Leerzustand mit Vektor-Grafik & Primär-CTA |
| **`FileUpload.svelte`** | [**`components/76-FileUpload.md`**](./components/76-FileUpload.md) | Drag & Drop Upload-Bereich für Labor-PDFs, CSVs & XML-Dateien |

### 1.3 Organismen & Visuelle Metaphern (*Visual Delight Engine*)
| Komponente | Datei / Detail-Spezifikation | Zweck |
|---|---|---|
| **`HeroProgressRings.svelte`** | [**`components/10-HeroProgressRings.md`**](./components/10-HeroProgressRings.md) | 3 konzentrische SVG-Ringe mit fließenden Glows & Zentrum-Icon |
| **`HydrationWaveGlass.svelte`** | [**`components/03-HydrationWaveGlass.md`**](./components/03-HydrationWaveGlass.md) | Füllendes SVG-Wasserglas mit oszillierenden Sinuswellen & Partikeln |
| **`MuscleHeatmap2D.svelte`** | [**`components/04-MuscleHeatmap2D.md`**](./components/04-MuscleHeatmap2D.md) | Anatomisches 2D-Muskelmodell (Front/Back) mit 7-Tage-Volumen-Heat |
| **`FastingMetabolicClock.svelte`** | [**`components/05-FastingMetabolicClock.md`**](./components/05-FastingMetabolicClock.md) | 360°-Kreis-Timer mit 4 leuchtenden Stoffwechsel-Zonen |
| **`CircadianSunArc.svelte`** | [**`components/11-CircadianSunArc.md`**](./components/11-CircadianSunArc.md) | 24h-Sonnenbogen mit Live-Zeiger, kognitiven Peaks & Koffein-Cutoff |
| **`MacroDonutGauge.svelte`** | [**`components/12-MacroDonutGauge.md`**](./components/12-MacroDonutGauge.md) | Dreifach verschachtelte Ringe für Protein, Carbs, Fett & Kalorien |
| **`SleepHypnogram.svelte`** | [**`components/13-SleepHypnogram.md`**](./components/13-SleepHypnogram.md) | Spline-Flächenkurve für Tief-, REM-, Leicht- & Wachschlaf |
| **`MoodValenceSphere.svelte`** | [**`components/14-MoodValenceSphere.md`**](./components/14-MoodValenceSphere.md) | 2D-Farbgradienten-Kugel, die sich nach Energie & Stimmung morpht |
| **`HabitYearMatrix.svelte`** | [**`components/31-HabitYearMatrix.md`**](./components/31-HabitYearMatrix.md) | 365-Tage GitHub-Style Jahres-Konsistenz-Matrix |
| **`RecipePortionCalculator.svelte`**| [**`components/38-RecipePortionCalculator.md`**](./components/38-RecipePortionCalculator.md)| Dynamischer Rezept- & Portions-Skalierer mit Makro-Neuberechnung |

### 1.4 Navigation, Shells, Dialoge & Overlays
| Komponente | Datei / Detail-Spezifikation | Zweck |
|---|---|---|
| **`TopAppBar.svelte`** | [**`components/07-TopAppBar.md`**](./components/07-TopAppBar.md) | Desktop Top-Leiste mit Breadcrumbs, Search (`Cmd+K`) & Profile-Pill |
| **`BottomNavBar.svelte`** | [**`components/08-BottomNavBar.md`**](./components/08-BottomNavBar.md) | Feste PWA-Navigationsleiste mit aktivem Glow & Center-FAB |
| **`QuickLogSheet.svelte`** | [**`components/01-QuickLogSheet.md`**](./components/01-QuickLogSheet.md) | Wischbares Bottom Sheet mit 1-Tap Aktionen & Ziffernblock |
| **`Modal.svelte`** | [**`components/54-Modal.md`**](./components/54-Modal.md) | Universeller barrierefreier Fokus-Dialog mit Backdrop-Blur |
| **`Drawer.svelte`** | [**`components/74-Drawer.md`**](./components/74-Drawer.md) | Multi-direktionales Slide-Over Panel (Left, Right, Bottom) |
| **`AlertDialog.svelte`** | [**`components/75-AlertDialog.md`**](./components/75-AlertDialog.md) | Destruktiver Bestätigungsdialog mit Fokus-Sicherheitslogik |
| **`CommandPalette.svelte`** | [**`components/09-CommandPalette.md`**](./components/09-CommandPalette.md) | Globale `Cmd+K` Spotlight-Suche & Befehlsleiste |
| **`NumericKeypad.svelte`** | [**`components/53-NumericKeypad.md`**](./components/53-NumericKeypad.md) | Taktiler Health-Ziffernblock mit Hantelscheiben-Quick-Adds |
| **`NotificationDrawer.svelte`**| [**`components/34-NotificationDrawer.md`**](./components/34-NotificationDrawer.md)| Slide-over Drawer für Zirkadian-Tipps, Meds & Rekorde |
| **`BarcodeScanner.svelte`** | [**`components/33-BarcodeScanner.md`**](./components/33-BarcodeScanner.md) | Kamera-Barcode-Scanner mit Fadenkreuz-Laser & Food-Lookup |
| **`WorkoutSetLogger.svelte`** | [**`components/28-WorkoutSetLogger.md`**](./components/28-WorkoutSetLogger.md) | Live-Satz-Erfassung mit Touchpads, Vorwochen-Referenz & RPE |
| **`JournalEditor.svelte`** | [**`components/44-JournalEditor.md`**](./components/44-JournalEditor.md) | Zen-Modus Markdown-Editor mit geführten Reflexionsfragen |
| **`ConflictResolver.svelte`** | [**`components/32-ConflictResolver.md`**](./components/32-ConflictResolver.md) | Feld-für-Feld visueller Offline-Konflikt-Auflöser |
| **`ToastManager.svelte`** | [**`components/46-ToastManager.md`**](./components/46-ToastManager.md) | Globaler Toast-Stack für Erfolgsmeldungen mit Undo-Button |

### 1.5 Datenvisualisierung & Tabellen-Analytik
| Komponente | Datei / Detail-Spezifikation | Zweck |
|---|---|---|
| **`InteractiveChart.svelte`** | [**`components/24-InteractiveChart.md`**](./components/24-InteractiveChart.md) | Hochpräzises SVG-Diagramm mit Scrubbing, 7T-EMA & Konfidenzband |
| **`DataTable.svelte`** | [**`components/68-DataTable.md`**](./components/68-DataTable.md) | Sortierbare, filterbare Tabelle mit Pagination & CSV-Export |
| **`BiomarkerHistoryTable.svelte`**| [**`components/36-BiomarkerHistoryTable.md`**](./components/36-BiomarkerHistoryTable.md)| Tabellarischer Labor-Vergleich über mehrere Blutentnahmen |
| **`Exercise1RMChart.svelte`** | [**`components/40-Exercise1RMChart.md`**](./components/40-Exercise1RMChart.md) | Dediziertes 1RM-Kraftkurven-Diagramm mit PR-Sternen |
| **`CorrelationMatrix.svelte`** | [**`components/25-CorrelationMatrix.md`**](./components/25-CorrelationMatrix.md) | Interaktive Korrelations-Heatmap mit Pearson r & Signifikanzen |
| **`ForecastSimulator.svelte`** | [**`components/26-ForecastSimulator.md`**](./components/26-ForecastSimulator.md) | Defizit- & Gewichts-Simulator mit 80%-Konfidenztrichter |

---

## 2. Detaillierte Props & Schnittstellen-Definitionen

### 2.1 `MetricTile.svelte`
```typescript
interface Props {
  title: string;
  value: string | number;
  unit?: string;
  color?: string;
  icon?: string;
  sparklineData?: number[];
  delta?: { value: string; positive: boolean; text: string };
  goalProgress?: { current: number; target: number; percent: number };
  size?: 'small' | 'medium' | 'large';
  onclick?: () => void;
}
```

### 2.2 `QuickLogSheet.svelte`
```typescript
interface Props {
  open: boolean;
  onclose: () => void;
  defaultTab?: 'water' | 'mood' | 'weight' | 'meal' | 'habit';
}
```

### 2.3 `HydrationWaveGlass.svelte`
```typescript
interface Props {
  currentMl: number;
  targetMl: number;
  onAdd: (deltaMl: number) => void;
}
```

### 2.4 `MuscleHeatmap2D.svelte`
```typescript
interface Props {
  volumeByMuscle: Record<string, number>; // z.B. { chest: 4500, back: 6200, quads: 8000 }
  view?: 'front' | 'back';
  interactive?: boolean;
  onSelectMuscle?: (muscleId: string) => void;
}
```

---

## 3. Barrierefreiheit & Interaktions-Standards

1. **Fokus-Management:** Alle interaktiven Elemente besitzen sichtbare, kontraststarke Fokus-Ringe (`outline: 2px solid var(--color-primary)`).
2. **ARIA-Labels:** Icons und Bild-Buttons haben zwingend eindeutige `aria-label`-Attribute.
3. **Keyboard Navigation:** Modals, Sheets und Menüs schließen bei `Escape` und fangen den Tab-Fokus (`Focus Trap`).
