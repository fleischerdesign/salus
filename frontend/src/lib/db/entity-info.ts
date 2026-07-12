import { getAuthHeaders } from '$lib/api/headers';

let _entityNames: Set<string> | null = null;

const HARDCODED_FALLBACK: Set<string> = new Set([
  'metric_type',
  'measurement',
  'goal',
  'circadian_profile',
  'exercise',
  'workout_plan',
  'workout_plan_exercise',
  'workout_session',
  'workout_log_entry',
  'insight',
  'notification',
  'dashboard_widget',
  'sharing_relationship',
  'leaderboard_group',
  'leaderboard_member',
  'share_recipient',
  'asymmetric_share',
  'user_profile',
  'admin_user',
  'admin_stats',
  'system_config',
  'api_token',
  'user',
  'community_activity',
  'federated_access_log'
]);

export async function fetchEntityNames(): Promise<Set<string>> {
  if (_entityNames) return _entityNames;

  try {
    const headers = { ...getAuthHeaders(), Accept: 'application/json' };
    const res = await fetch('/api/v1/sync/entities', { headers });
    if (res.ok) {
      const data = (await res.json()) as Array<{ name: string }>;
      _entityNames = new Set(data.map((e) => e.name));
      return _entityNames;
    }
  } catch {
    /* fall back to hardcoded list */
  }

  _entityNames = HARDCODED_FALLBACK;
  return _entityNames;
}

export function getEntityNames(): Set<string> {
  return _entityNames ?? HARDCODED_FALLBACK;
}

export function resetEntityNames(): void {
  _entityNames = null;
}
