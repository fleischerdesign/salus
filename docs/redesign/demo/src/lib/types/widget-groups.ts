export type WidgetType =
  | 'custom_group'
  | 'circadian_arc'
  | 'blood_pressure_dial'
  | 'rhr_sparkline'
  | 'spo2_vo2max'
  | 'cgm_wave'
  | 'time_in_range'
  | 'fasting_transition'
  | 'fasting_clock'
  | 'recovery_battery'
  | 'ans_balance'
  | 'sleep_hypnogram'
  | 'bia_spectrum'
  | 'whtr_gauge'
  | 'hydration_glass'
  | 'activity_histogram'
  | 'tdee_split'
  | 'hero_rings'
  | 'mood_sphere'
  | 'medication_dose'
  | 'habits_pills'
  | 'habits_year';

export interface DashboardWidget {
  id: string;
  type: WidgetType;
  title: string;
  size?: 'full' | 'half' | 'third';
}

export interface DashboardWidgetGroup {
  id: string;
  title: string;
  subtitle?: string;
  icon?: string;
  collapsed?: boolean;
  columns: 1 | 2 | 3;
  widgets: DashboardWidget[];
}

export type DashboardItem =
  | { id: string; kind: 'widget'; widget: DashboardWidget }
  | { id: string; kind: 'group'; group: DashboardWidgetGroup };

export const WIDGET_CATALOG: {
  type: WidgetType;
  title: string;
  description: string;
  category: 'Layout' | 'Kardiovaskulär' | 'Stoffwechsel' | 'Erholung' | 'Körper' | 'Aktivität' | 'Lifestyle';
  defaultSize: 'full' | 'half' | 'third';
  isGroupTemplate?: boolean;
}[] = [
  // ─── 0. LAYOUT & GRUPPEN ───
  {
    type: 'custom_group',
    title: 'Visuelle Widget-Gruppe (Abschnitt)',
    description: 'Erstelle eine neue gruppierte Sektion mit individuellem Titel, Untertitel und Spalten-Raster (1–3 Spalten).',
    category: 'Layout',
    defaultSize: 'full',
    isGroupTemplate: true
  },

  // ─── 1. ERHOLUNG & ZIRKADIAN ───
  {
    type: 'circadian_arc',
    title: 'Zirkadianer 24h-Sonnenbogen',
    description: 'NOAA Sonnenzeiten, Alignment-Score und physiologische Zeitfenster',
    category: 'Erholung',
    defaultSize: 'full'
  },
  {
    type: 'recovery_battery',
    title: 'ZNS-Erholungsbatterie',
    description: '88% Recovery Ring und empfohlener Tages-Strain',
    category: 'Erholung',
    defaultSize: 'half'
  },
  {
    type: 'ans_balance',
    title: 'Autonome Nervensystem-Balance',
    description: 'Parasympathikus vs. Sympathikus Verhältnis',
    category: 'Erholung',
    defaultSize: 'half'
  },
  {
    type: 'sleep_hypnogram',
    title: 'Schlafarchitektur und Schlafschuld',
    description: 'Hypnogramm, Schlafphasen und 30T-Schlafschuld',
    category: 'Erholung',
    defaultSize: 'half'
  },

  // ─── 2. KARDIOVASKULÄR ───
  {
    type: 'blood_pressure_dial',
    title: 'Arterieller Blutdruck (ESC 2024)',
    description: 'Systolisch/Diastolisch mit Mehrzonen-Skala und Pulsdruck',
    category: 'Kardiovaskulär',
    defaultSize: 'half'
  },
  {
    type: 'rhr_sparkline',
    title: 'Ruhepuls (7T-Trend)',
    description: 'Ruheherzfrequenz mit Monatsvergleich und Sparkline',
    category: 'Kardiovaskulär',
    defaultSize: 'half'
  },
  {
    type: 'spo2_vo2max',
    title: 'SpO2 und VO2 Max Fitness',
    description: 'Sauerstoffsättigung und Ausdauer-Perzentil',
    category: 'Kardiovaskulär',
    defaultSize: 'half'
  },

  // ─── 3. STOFFWECHSEL ───
  {
    type: 'cgm_wave',
    title: 'Kontinuierliche Glukosekurve (CGM)',
    description: '24h Blutzuckerspline mit 70–140 mg/dL Zielkorridor',
    category: 'Stoffwechsel',
    defaultSize: 'half'
  },
  {
    type: 'time_in_range',
    title: 'Time in Range (TIR)',
    description: 'Stunden und Prozent im optimalen Glukosebereich',
    category: 'Stoffwechsel',
    defaultSize: 'half'
  },
  {
    type: 'fasting_transition',
    title: 'Fasten-Metabolismus',
    description: 'Autophagie und Ketogenese Übergangsanzeige',
    category: 'Stoffwechsel',
    defaultSize: 'half'
  },
  {
    type: 'fasting_clock',
    title: '16:8 Fasten-Stoffwechseluhr',
    description: 'Live-Timer mit metabolischen Phasen',
    category: 'Stoffwechsel',
    defaultSize: 'third'
  },

  // ─── 4. KÖRPER & ANTHROPOMETRIE ───
  {
    type: 'bia_spectrum',
    title: 'BIA-Zusammensetzungsspektrum',
    description: 'Fettfreie Muskelmasse vs. Depotfett und Wasser',
    category: 'Körper',
    defaultSize: 'half'
  },
  {
    type: 'whtr_gauge',
    title: 'Waist-to-Height Ratio (WHtR)',
    description: 'Taillenumfang und kardiometabolischer Index',
    category: 'Körper',
    defaultSize: 'half'
  },
  {
    type: 'hydration_glass',
    title: 'Hydration Wave Glass',
    description: 'Animiertes Wasserglas mit 1-Tap Protokollierung',
    category: 'Körper',
    defaultSize: 'third'
  },

  // ─── 5. AKTIVITÄT ───
  {
    type: 'activity_histogram',
    title: 'Diurnales Schritt-Histogramm',
    description: 'Stündliche Aktivitäts-Peaks über 24 Stunden',
    category: 'Aktivität',
    defaultSize: 'half'
  },
  {
    type: 'tdee_split',
    title: 'TDEE Energieumsatz-Split',
    description: 'Aktiver Kalorienverbrauch vs. Basal Metabolic Rate',
    category: 'Aktivität',
    defaultSize: 'half'
  },

  // ─── 6. LIFESTYLE & HABITS ───
  {
    type: 'hero_rings',
    title: 'Biometrische Progress-Ringe',
    description: 'Fortschrittsringe für Bewegung, Fasten und Wasser',
    category: 'Lifestyle',
    defaultSize: 'half'
  },
  {
    type: 'mood_sphere',
    title: 'Psychobiometrische Valenz-Sphäre',
    description: '2D Stimmungs- und Erregungskoordinaten',
    category: 'Lifestyle',
    defaultSize: 'half'
  },
  {
    type: 'medication_dose',
    title: 'Medikamenten- und Supplementeplan',
    description: 'Tagesdosen mit Einnahmezeiten und Refill-Status',
    category: 'Lifestyle',
    defaultSize: 'half'
  },
  {
    type: 'habits_pills',
    title: 'Tages-Gewohnheiten Checkliste',
    description: 'Interaktive 1-Tap Habit-Pills mit Streaks',
    category: 'Lifestyle',
    defaultSize: 'full'
  },
  {
    type: 'habits_year',
    title: '52-Wochen Konsistenz-Matrix',
    description: 'GitHub-Style Heatmap für alle Gewohnheiten',
    category: 'Lifestyle',
    defaultSize: 'full'
  }
];
