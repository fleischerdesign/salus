import { resolveColor } from './colors';
import type { MetricDefinition, UserMetricPreference, MetricWithPreference } from '$lib/db/types';

/**
 * Merges metric definitions with per-user preferences, resolving the category
 * color through resolveColor for the active accessibility mode.
 */
export function mergeMetricPrefs(
  definitions: MetricDefinition[],
  preferences: UserMetricPreference[],
  defaultIcon: string = 'monitoring'
): MetricWithPreference[] {
  const prefMap = new Map(preferences.map((p) => [p.metric_code, p]));
  return definitions.map((def) => {
    const pref = prefMap.get(def.code);
    return {
      ...def,
      color: resolveColor(pref?.color ?? '#4f46e5'),
      icon: pref?.icon ?? defaultIcon,
      widget_size: pref?.widget_size ?? 'medium',
      widget_enabled: pref?.widget_enabled ?? false,
      enabled: pref?.enabled ?? true,
      position: pref?.position ?? 0
    };
  });
}
