const HIDDEN_FIELDS = new Set([
  'password_hash',
  'token_hash',
  'api_token_hash',
  'encrypted_key',
  'encrypted_data'
]);

const SKIP_FIELDS = new Set([
  'id',
  'created_at',
  'updated_at',
  'deleted_at',
  'last_used_at',
  'last_sync_at',
  'accessed_at'
]);

export interface DiffRow {
  field: string;
  client: unknown;
  server: unknown;
}

export function computeDiff(
  client: Record<string, unknown>,
  server: Record<string, unknown>
): DiffRow[] {
  const allKeys = new Set([...Object.keys(client), ...Object.keys(server)]);
  const rows: DiffRow[] = [];

  for (const key of allKeys) {
    if (HIDDEN_FIELDS.has(key)) continue;
    if (SKIP_FIELDS.has(key)) continue;

    if (key.startsWith('_')) continue;

    const cv = client[key];
    const sv = server[key];

    if (JSON.stringify(cv) === JSON.stringify(sv)) continue;

    rows.push({ field: key, client: cv, server: sv });
  }

  return rows;
}

export function formatValue(v: unknown): string {
  if (v === null || v === undefined) return '\u2014';
  if (typeof v === 'boolean') return v ? 'Yes' : 'No';
  if (typeof v === 'number') return v.toLocaleString();

  if (typeof v === 'string') {
    const ts = Date.parse(v);
    if (!isNaN(ts) && v.match(/^\d{4}-\d{2}-\d{2}/)) {
      return new Date(v).toLocaleString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
    return v;
  }

  if (typeof v === 'object') {
    try {
      return JSON.stringify(v);
    } catch {
      return String(v);
    }
  }

  return String(v);
}

const ENTITY_LABELS: Record<string, string> = {
  metric_group: 'Metric Group',
  metric_definition: 'Metric Definition',
  user_metric_preference: 'Metric Preference',
  measurement: 'Measurement',
  goal: 'Goal',
  circadian_profile: 'Circadian Profile',
  exercise: 'Exercise',
  workout_plan: 'Workout Plan',
  workout_plan_exercise: 'Plan Exercise',
  workout_session: 'Workout Session',
  workout_log_entry: 'Log Entry',
  insight: 'Insight',
  notification: 'Notification',
  dashboard_widget: 'Dashboard Widget',
  sharing_relationship: 'Sharing Relationship',
  leaderboard_group: 'Leaderboard Group',
  leaderboard_member: 'Leaderboard Member',
  share_recipient: 'Share Recipient',
  asymmetric_share: 'Share',
  user: 'User Profile',
  user_profile: 'User Profile',
  api_token: 'API Token'
};

export function entityLabel(table: string): string {
  return ENTITY_LABELS[table] ?? table;
}
