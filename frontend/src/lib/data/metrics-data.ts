import type { MetricGroup, MetricDefinition } from '../types';

export interface MetricCategoryInfo {
  id: string;
  label: string;
  icon: string;
}

export const METRIC_CATEGORIES: MetricCategoryInfo[] = [
  { id: 'all', label: 'Alle Metriken', icon: 'grid-view' },
  { id: 'cardiovascular', label: 'Kardiovaskulär', icon: 'vital-signs' },
  { id: 'body', label: 'Körper & Gewicht', icon: 'scale' },
  { id: 'metabolism', label: 'Stoffwechsel', icon: 'science' },
  { id: 'activity', label: 'Aktivität & Fitness', icon: 'directions-run' },
  { id: 'sleep', label: 'Schlaf & Erholung', icon: 'bedtime' },
  { id: 'labs', label: 'Klinische Labore', icon: 'biotech' }
];

/**
 * Genuine functional metric groups (e.g. combined forms or strictly bound sub-metrics).
 */
export const METRIC_GROUPS: MetricGroup[] = [
  {
    key: 'blood_pressure',
    title: 'Arterieller Blutdruck',
    category: 'cardiovascular',
    inputMode: 'combined',
    description:
      'Systolischer & Diastolischer Blutdruck nach europäischen ESC/ESH 2024 Leitlinien.',
    subMetrics: [
      {
        code: 'systolic_bp',
        name: 'Systolischer Blutdruck',
        unit: 'mmHg',
        category: 'cardiovascular',
        dataType: 'number',
        groupKey: 'blood_pressure',
        currentValue: 118,
        previousValue: 122,
        deltaPercent: -3.2,
        trend: 'improving',
        referenceRange: '< 120 mmHg (ESC 2024)',
        optimalRange: { min: 105, max: 120 },
        ema7d: 119.2,
        sparklineData: [124, 122, 120, 121, 119, 118, 118]
      },
      {
        code: 'diastolic_bp',
        name: 'Diastolischer Blutdruck',
        unit: 'mmHg',
        category: 'cardiovascular',
        dataType: 'number',
        groupKey: 'blood_pressure',
        currentValue: 76,
        previousValue: 79,
        deltaPercent: -3.8,
        trend: 'improving',
        referenceRange: '< 80 mmHg (ESC 2024)',
        optimalRange: { min: 70, max: 80 },
        ema7d: 76.8,
        sparklineData: [80, 78, 79, 77, 76, 76, 76]
      }
    ]
  },
  {
    key: 'body_measurements',
    title: 'Körperumfänge & Anthropometrie',
    category: 'body',
    inputMode: 'individual',
    description: 'Umfangsmessungen für Taille, Hüfte, Brust und Extremitäten.',
    subMetrics: [
      {
        code: 'waist',
        name: 'Taillenumfang',
        unit: 'cm',
        category: 'body',
        dataType: 'number',
        groupKey: 'body_measurements',
        currentValue: 84.0,
        previousValue: 85.5,
        deltaPercent: -1.7,
        trend: 'improving',
        referenceRange: '< 94 cm (Männer) / < 80 cm (Frauen)',
        optimalRange: { min: 75, max: 88 },
        ema7d: 84.5,
        sparklineData: [86.0, 85.5, 85.0, 84.8, 84.5, 84.2, 84.0]
      },
      {
        code: 'hip',
        name: 'Hüftumfang',
        unit: 'cm',
        category: 'body',
        dataType: 'number',
        groupKey: 'body_measurements',
        currentValue: 98.0,
        previousValue: 99.0,
        deltaPercent: -1.0,
        trend: 'improving',
        referenceRange: 'WH-Ratio < 0.9',
        optimalRange: { min: 92, max: 102 },
        ema7d: 98.5,
        sparklineData: [99.5, 99.0, 98.8, 98.5, 98.2, 98.0, 98.0]
      },
      {
        code: 'chest',
        name: 'Brustumfang',
        unit: 'cm',
        category: 'body',
        dataType: 'number',
        groupKey: 'body_measurements',
        currentValue: 104.0,
        previousValue: 103.5,
        deltaPercent: 0.5,
        trend: 'improving',
        referenceRange: 'Athletischer Aufbau',
        optimalRange: { min: 98, max: 112 },
        ema7d: 103.8,
        sparklineData: [103.0, 103.2, 103.5, 103.8, 104.0, 104.0, 104.0]
      },
      {
        code: 'thigh',
        name: 'Oberschenkelumfang',
        unit: 'cm',
        category: 'body',
        dataType: 'number',
        groupKey: 'body_measurements',
        currentValue: 58.5,
        previousValue: 58.0,
        deltaPercent: 0.8,
        trend: 'improving',
        referenceRange: 'Kraftaufbau',
        optimalRange: { min: 54, max: 64 },
        ema7d: 58.2,
        sparklineData: [57.8, 58.0, 58.2, 58.3, 58.4, 58.5, 58.5]
      },
      {
        code: 'biceps',
        name: 'Oberarmumfang',
        unit: 'cm',
        category: 'body',
        dataType: 'number',
        groupKey: 'body_measurements',
        currentValue: 36.5,
        previousValue: 36.0,
        deltaPercent: 1.4,
        trend: 'improving',
        referenceRange: 'Kraftaufbau',
        optimalRange: { min: 34, max: 42 },
        ema7d: 36.2,
        sparklineData: [35.8, 36.0, 36.2, 36.4, 36.5, 36.5, 36.5]
      }
    ]
  },
  {
    key: 'lipid_panel',
    title: 'Lipidprofil & Cholesterin',
    category: 'labs',
    inputMode: 'individual',
    description: 'Gesamtcholesterin, HDL, LDL und Triglyceride.',
    subMetrics: [
      {
        code: 'cholesterol_total',
        name: 'Gesamtcholesterin',
        unit: 'mg/dL',
        category: 'labs',
        dataType: 'number',
        groupKey: 'lipid_panel',
        currentValue: 178,
        previousValue: 185,
        deltaPercent: -3.8,
        trend: 'improving',
        referenceRange: '< 200 mg/dL',
        optimalRange: { min: 140, max: 190 },
        ema7d: 178.0,
        sparklineData: [195, 190, 185, 182, 180, 178, 178]
      },
      {
        code: 'ldl',
        name: 'LDL-Cholesterin',
        unit: 'mg/dL',
        category: 'labs',
        dataType: 'number',
        groupKey: 'lipid_panel',
        currentValue: 92,
        previousValue: 98,
        deltaPercent: -6.1,
        trend: 'improving',
        referenceRange: '< 100 mg/dL (Optimal)',
        optimalRange: { min: 60, max: 95 },
        ema7d: 92.0,
        sparklineData: [105, 102, 98, 96, 94, 92, 92]
      },
      {
        code: 'hdl',
        name: 'HDL-Cholesterin',
        unit: 'mg/dL',
        category: 'labs',
        dataType: 'number',
        groupKey: 'lipid_panel',
        currentValue: 64,
        previousValue: 62,
        deltaPercent: 3.2,
        trend: 'improving',
        referenceRange: '> 50 mg/dL (Protektiv)',
        optimalRange: { min: 55, max: 85 },
        ema7d: 64.0,
        sparklineData: [58, 60, 62, 63, 63, 64, 64]
      },
      {
        code: 'triglycerides',
        name: 'Triglyceride',
        unit: 'mg/dL',
        category: 'labs',
        dataType: 'number',
        groupKey: 'lipid_panel',
        currentValue: 88,
        previousValue: 95,
        deltaPercent: -7.4,
        trend: 'improving',
        referenceRange: '< 150 mg/dL',
        optimalRange: { min: 50, max: 100 },
        ema7d: 88.0,
        sparklineData: [110, 105, 95, 92, 90, 88, 88]
      }
    ]
  }
];

/**
 * Standalone individual metrics that exist as independent time-series.
 */
export const STANDALONE_METRICS: MetricDefinition[] = [
  // ─── 1. KARDIOVASKULÄR ──────────────────────────────────────────────────
  {
    code: 'heart_rate',
    name: 'Herzfrequenz (Puls)',
    unit: 'bpm',
    category: 'cardiovascular',
    dataType: 'number',
    currentValue: 72,
    previousValue: 75,
    deltaPercent: -4.0,
    trend: 'stable',
    referenceRange: '60–100 bpm',
    optimalRange: { min: 50, max: 80 },
    ema7d: 71.5,
    sparklineData: [74, 73, 76, 72, 70, 71, 72]
  },
  {
    code: 'resting_heart_rate',
    name: 'Ruhepuls (RHR)',
    unit: 'bpm',
    category: 'cardiovascular',
    dataType: 'number',
    currentValue: 64,
    previousValue: 66,
    deltaPercent: -3.0,
    trend: 'improving',
    referenceRange: '50–75 bpm',
    optimalRange: { min: 50, max: 65 },
    ema7d: 64.5,
    sparklineData: [68, 66, 65, 65, 64, 64, 64]
  },
  {
    code: 'hrv',
    name: 'Herzfrequenzvariabilität (HRV)',
    unit: 'ms',
    category: 'cardiovascular',
    dataType: 'number',
    currentValue: 68,
    previousValue: 58,
    deltaPercent: 17.2,
    trend: 'improving',
    referenceRange: '> 40 ms (rMSSD)',
    optimalRange: { min: 50, max: 100 },
    ema7d: 65.0,
    sparklineData: [52, 58, 60, 62, 65, 66, 68]
  },
  {
    code: 'spo2',
    name: 'Blutsauerstoff (SpO2)',
    unit: '%',
    category: 'cardiovascular',
    dataType: 'number',
    currentValue: 98,
    previousValue: 97,
    deltaPercent: 1.0,
    trend: 'stable',
    referenceRange: '≥ 95%',
    optimalRange: { min: 95, max: 100 },
    ema7d: 97.8,
    sparklineData: [97, 98, 97, 98, 98, 98, 98]
  },
  {
    code: 'respiratory_rate',
    name: 'Atemfrequenz',
    unit: 'rpm',
    category: 'cardiovascular',
    dataType: 'number',
    currentValue: 14,
    previousValue: 15,
    deltaPercent: -6.7,
    trend: 'stable',
    referenceRange: '12–20 rpm',
    optimalRange: { min: 12, max: 16 },
    ema7d: 14.2,
    sparklineData: [15, 14, 15, 14, 14, 14, 14]
  },

  // ─── 2. KÖRPER & ANTHROPOMETRIE ──────────────────────────────────────────
  {
    code: 'weight',
    name: 'Körpergewicht',
    unit: 'kg',
    category: 'body',
    dataType: 'number',
    currentValue: 81.8,
    previousValue: 82.5,
    deltaPercent: -0.8,
    trend: 'improving',
    referenceRange: 'Ziel: 78–80 kg',
    optimalRange: { min: 78, max: 80 },
    ema7d: 82.0,
    sparklineData: [83.2, 82.8, 82.5, 82.9, 82.2, 81.9, 81.8]
  },
  {
    code: 'body_fat',
    name: 'Körperfettanteil (KFA)',
    unit: '%',
    category: 'body',
    dataType: 'number',
    currentValue: 16.4,
    previousValue: 16.9,
    deltaPercent: -3.0,
    trend: 'improving',
    referenceRange: '10–20% (Athletisch)',
    optimalRange: { min: 10, max: 18 },
    ema7d: 16.6,
    sparklineData: [17.5, 17.2, 16.9, 16.8, 16.6, 16.5, 16.4]
  },
  {
    code: 'lean_body_mass',
    name: 'Fettfreie Masse (Muskelmasse)',
    unit: 'kg',
    category: 'body',
    dataType: 'number',
    currentValue: 68.4,
    previousValue: 68.1,
    deltaPercent: 0.4,
    trend: 'improving',
    referenceRange: 'Kraftaufbau',
    optimalRange: { min: 66, max: 74 },
    ema7d: 68.3,
    sparklineData: [67.8, 68.0, 68.1, 68.2, 68.3, 68.4, 68.4]
  },
  {
    code: 'bone_mass',
    name: 'Knochenmasse',
    unit: 'kg',
    category: 'body',
    dataType: 'number',
    currentValue: 3.4,
    previousValue: 3.4,
    deltaPercent: 0.0,
    trend: 'stable',
    referenceRange: '2.8–3.8 kg',
    optimalRange: { min: 3.0, max: 3.8 },
    ema7d: 3.4,
    sparklineData: [3.4, 3.4, 3.4, 3.4, 3.4, 3.4, 3.4]
  },
  {
    code: 'body_temperature',
    name: 'Körpertemperatur',
    unit: '°C',
    category: 'body',
    dataType: 'number',
    currentValue: 36.8,
    previousValue: 36.7,
    deltaPercent: 0.3,
    trend: 'stable',
    referenceRange: '36.5–37.5 °C',
    optimalRange: { min: 36.4, max: 37.2 },
    ema7d: 36.8,
    sparklineData: [36.7, 36.8, 36.7, 36.9, 36.8, 36.8, 36.8]
  },

  // ─── 3. AKTIVITÄT & FITNESS ──────────────────────────────────────────────
  {
    code: 'steps',
    name: 'Schritte',
    unit: 'steps',
    category: 'activity',
    dataType: 'number',
    currentValue: 10450,
    previousValue: 8900,
    deltaPercent: 17.4,
    trend: 'improving',
    referenceRange: '≥ 10.000 Schritte',
    optimalRange: { min: 8000, max: 15000 },
    ema7d: 9800,
    sparklineData: [8500, 9200, 8900, 11200, 10800, 9500, 10450]
  },
  {
    code: 'active_calories',
    name: 'Aktivitätskalorien',
    unit: 'kcal',
    category: 'activity',
    dataType: 'number',
    currentValue: 540,
    previousValue: 480,
    deltaPercent: 12.5,
    trend: 'improving',
    referenceRange: '≥ 500 kcal',
    optimalRange: { min: 400, max: 800 },
    ema7d: 510,
    sparklineData: [450, 480, 520, 560, 490, 510, 540]
  },
  {
    code: 'distance',
    name: 'Distanz',
    unit: 'km',
    category: 'activity',
    dataType: 'number',
    currentValue: 7.8,
    previousValue: 6.5,
    deltaPercent: 20.0,
    trend: 'improving',
    referenceRange: '≥ 5.0 km',
    optimalRange: { min: 5.0, max: 12.0 },
    ema7d: 7.2,
    sparklineData: [6.0, 6.5, 7.0, 8.2, 7.5, 6.8, 7.8]
  },
  {
    code: 'vo2_max',
    name: 'VO2max (Kardiorespiratorische Fitness)',
    unit: 'ml/kg/min',
    category: 'activity',
    dataType: 'number',
    currentValue: 48.5,
    previousValue: 47.8,
    deltaPercent: 1.5,
    trend: 'improving',
    referenceRange: '> 42 ml/kg/min (Perzentil > 80%)',
    optimalRange: { min: 45, max: 60 },
    ema7d: 48.2,
    sparklineData: [46.5, 47.0, 47.5, 47.8, 48.0, 48.2, 48.5]
  },
  {
    code: 'floors_climbed',
    name: 'Stockwerke',
    unit: 'Etagen',
    category: 'activity',
    dataType: 'number',
    currentValue: 14,
    previousValue: 10,
    deltaPercent: 40.0,
    trend: 'improving',
    referenceRange: '≥ 10 Etagen',
    optimalRange: { min: 10, max: 25 },
    ema7d: 12,
    sparklineData: [8, 10, 12, 15, 11, 13, 14]
  },

  // ─── 4. STOFFWECHSEL & GLUKOSE ──────────────────────────────────────────
  {
    code: 'blood_glucose',
    name: 'Blutzucker (Glukose)',
    unit: 'mg/dL',
    category: 'metabolism',
    dataType: 'number',
    currentValue: 88,
    previousValue: 92,
    deltaPercent: -4.3,
    trend: 'improving',
    referenceRange: '70–99 mg/dL (Nüchtern)',
    optimalRange: { min: 72, max: 95 },
    ema7d: 89.5,
    sparklineData: [94, 91, 92, 88, 90, 89, 88]
  },
  {
    code: 'hba1c',
    name: 'Langzeitblutzucker (HbA1c)',
    unit: '%',
    category: 'metabolism',
    dataType: 'number',
    currentValue: 5.1,
    previousValue: 5.2,
    deltaPercent: -1.9,
    trend: 'improving',
    referenceRange: '< 5.7% (Normbereich)',
    optimalRange: { min: 4.8, max: 5.4 },
    ema7d: 5.1,
    sparklineData: [5.3, 5.3, 5.2, 5.2, 5.1, 5.1, 5.1]
  },
  {
    code: 'ketones',
    name: 'Blutketone (BHB)',
    unit: 'mmol/L',
    category: 'metabolism',
    dataType: 'number',
    currentValue: 1.2,
    previousValue: 0.8,
    deltaPercent: 50.0,
    trend: 'improving',
    referenceRange: '0.5–3.0 mmol/L (Ernährungsketose)',
    optimalRange: { min: 0.5, max: 2.5 },
    ema7d: 1.0,
    sparklineData: [0.4, 0.6, 0.8, 1.0, 1.1, 1.2, 1.2]
  },
  {
    code: 'water',
    name: 'Wasseraufnahme',
    unit: 'ml',
    category: 'metabolism',
    dataType: 'number',
    currentValue: 2450,
    previousValue: 2100,
    deltaPercent: 16.7,
    trend: 'improving',
    referenceRange: '2.500–3.500 ml',
    optimalRange: { min: 2500, max: 3500 },
    ema7d: 2380,
    sparklineData: [2000, 2200, 2100, 2600, 2500, 2300, 2450]
  },

  // ─── 5. SCHLAF & ERHOLUNG ────────────────────────────────────────────────
  {
    code: 'sleep_duration',
    name: 'Schlafdauer',
    unit: 'min',
    category: 'sleep',
    dataType: 'number',
    currentValue: 465,
    previousValue: 440,
    deltaPercent: 5.7,
    trend: 'improving',
    referenceRange: '420–540 min (7–9 Stunden)',
    optimalRange: { min: 420, max: 540 },
    ema7d: 455,
    sparklineData: [430, 445, 440, 480, 460, 450, 465]
  },
  {
    code: 'sleep_score',
    name: 'Schlaf-Score',
    unit: '%',
    category: 'sleep',
    dataType: 'number',
    currentValue: 88,
    previousValue: 82,
    deltaPercent: 7.3,
    trend: 'improving',
    referenceRange: '≥ 85% (Optimale Erholung)',
    optimalRange: { min: 85, max: 100 },
    ema7d: 86.2,
    sparklineData: [80, 84, 82, 90, 87, 85, 88]
  }
];

/**
 * Lookup helper: Finds a metric definition by its unique code (checks standalone + all groups).
 */
export function findMetricDefinition(code: string): MetricDefinition | undefined {
  const direct = STANDALONE_METRICS.find((m) => m.code === code);
  if (direct) return direct;

  for (const g of METRIC_GROUPS) {
    const sub = g.subMetrics.find((m) => m.code === code);
    if (sub) return sub;
  }
  return undefined;
}

/**
 * Lookup helper: Finds a metric group by its unique key.
 */
export function findMetricGroup(key: string): MetricGroup | undefined {
  return METRIC_GROUPS.find((g) => g.key === key);
}

/**
 * Returns all registered metric definitions (both standalone and group sub-metrics).
 */
export function getAllMetrics(): MetricDefinition[] {
  const groupSubMetrics = METRIC_GROUPS.flatMap((g) => g.subMetrics);
  return [...STANDALONE_METRICS, ...groupSubMetrics];
}
