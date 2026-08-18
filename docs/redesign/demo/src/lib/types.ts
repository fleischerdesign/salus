export type PageId =
  | 'dashboard'
  | 'track'
  | 'klinik'
  | 'community'
  | 'insights'
  | 'metrics-overview'
  | 'metric-group-detail'
  | 'metric-single-detail'
  | 'workouts'
  | 'workouts-active'
  | 'workouts-plans'
  | 'workouts-sessions'
  | 'workouts-exercises'
  | 'food'
  | 'food-diary'
  | 'food-recipes'
  | 'food-database'
  | 'fasting'
  | 'goals'
  | 'coach'
  | 'achievements'
  | 'labs'
  | 'journal'
  | 'medications'
  | 'community-leaderboard'
  | 'community-connections'
  | 'community-feed'
  | 'community-audit'
  | 'open-science'
  | 'habits'
  | 'settings'
  | 'admin';

export type ViewId = PageId;

export interface MetricDefinition {
  code: string;
  name: string;
  unit: string;
  category: 'cardiovascular' | 'body' | 'metabolism' | 'sleep' | 'activity' | 'labs' | 'mental';
  dataType: 'number' | 'text';
  groupKey?: string;
  currentValue: number | string;
  previousValue?: number | string;
  deltaPercent?: number;
  trend: 'improving' | 'stable' | 'worsening';
  referenceRange?: string;
  optimalRange?: { min: number; max: number };
  ema7d?: number;
  sparklineData: number[];
}

export interface MetricGroup {
  key: string;
  title: string;
  category: 'cardiovascular' | 'body' | 'metabolism' | 'sleep' | 'activity' | 'labs' | 'mental';
  inputMode: 'combined' | 'individual';
  description: string;
  subMetrics: MetricDefinition[];
}

export interface MeasurementEntry {
  id: string;
  metricCode: string;
  value: number;
  unit: string;
  timestamp: string;
  source: 'manual' | 'healthkit' | 'wearable' | 'lab_import';
  note?: string;
}

export interface HabitItem {
  id: string;
  name: string;
  streakDays: number;
  completedToday: boolean;
}

export interface WorkoutSet {
  setNumber: number;
  previous: string;
  weightKg: number;
  reps: number;
  rpe: string;
  completed: boolean;
}

export interface BiomarkerRow {
  name: string;
  reference: string;
  currentMgDl: number;
  currentMmol: number;
  oldMgDl: number;
  oldMmol: number;
  unitMgDl: string;
  unitMmol: string;
  trend: string;
  isOptimal: boolean;
}
