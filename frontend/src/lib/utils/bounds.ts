export interface MetricBounds {
  min_value: number | null;
  max_value: number | null;
  unit: string;
}

/**
 * Non-blocking hint when a value falls outside the metric's plausible bounds.
 * Returns null when the value is empty, non-numeric, or in range.
 */
export function boundHint(value: string, metric: MetricBounds): string | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const numeric = Number(trimmed);
  if (isNaN(numeric)) return null;
  const low = metric.min_value != null && numeric < metric.min_value;
  const high = metric.max_value != null && numeric > metric.max_value;
  if (!low && !high) return null;
  const range = `${metric.min_value ?? '−∞'}–${metric.max_value ?? '∞'} ${metric.unit}`.trim();
  return `Unusual value — plausible range is ${range}`;
}
