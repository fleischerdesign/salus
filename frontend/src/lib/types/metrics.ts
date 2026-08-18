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
