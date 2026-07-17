export type OutboxKind = 'crud' | 'command';

export interface OutboxCrudOp {
  id?: number;
  kind: 'crud';
  opType: 'create' | 'update' | 'delete';
  entity: string;
  client_id: string;
  data?: Record<string, unknown>;
  realId?: string;
  expected_updated_at?: string;
  createdAt: string;
  retries: number;
}

export interface OutboxCommandOp {
  id?: number;
  kind: 'command';
  command: string;
  client_id: string;
  payload?: Record<string, unknown>;
  optimisticTable?: string;
  optimisticData?: Record<string, unknown>;
  responseTable?: string;
  createdAt: string;
  retries: number;
}

export type OutboxOp = OutboxCrudOp | OutboxCommandOp;

export type SyncStatus = 'idle' | 'syncing' | 'error';

export interface SyncMeta {
  key: string;
  value: unknown;
}

export interface MetricDefinition {
  code: string;
  name: string;
  unit: string;
  data_type: string;
  source_data_type: string | null;
  group_key: string | null;
  description: string | null;
  sort_order: number;
}

export interface MetricGroup {
  key: string;
  name: string;
  icon: string;
  description: string | null;
  input_mode: string;
}

export interface UserMetricPreference {
  id: string;
  user_id: string;
  metric_code: string;
  enabled: boolean;
  color: string;
  icon: string;
  widget_size: string;
  widget_enabled: boolean;
  position: number;
}

export interface MetricWithPreference extends MetricDefinition {
  color: string;
  icon: string;
  widget_size: string;
  widget_enabled: boolean;
  enabled: boolean;
  position: number;
}

export function mergeMetricPrefs(
  definitions: MetricDefinition[],
  preferences: UserMetricPreference[]
): MetricWithPreference[] {
  const prefMap = new Map(preferences.map((p) => [p.metric_code, p]));
  return definitions.map((def) => {
    const pref = prefMap.get(def.code);
    return {
      ...def,
      color: pref?.color ?? '#4f46e5',
      icon: pref?.icon ?? 'monitoring',
      widget_size: pref?.widget_size ?? 'medium',
      widget_enabled: pref?.widget_enabled ?? false,
      enabled: pref?.enabled ?? true,
      position: pref?.position ?? 0
    };
  });
}

export interface Measurement {
  id: string;
  user_id: string;
  metric_code: string | null;
  data_type: string;
  source: string;
  value_numeric: number | null;
  value_text: string | null;
  value_json: string | null;
  start_time: string;
  end_time: string | null;
  notes: string | null;
  external_id: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Goal {
  id: string;
  user_id: string;
  metric_code: string;
  target_value: number;
  direction: string;
  frequency: string;
  deadline: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface CircadianProfile {
  id: string;
  user_id: string;
  latitude: number;
  longitude: number;
  timezone_offset_hours: number;
  configured_chronotype: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Exercise {
  id: string;
  name: string;
  equipment: string | null;
  primary_muscles: string | null;
  secondary_muscles: string | null;
  description: string | null;
  instructions: string | null;
  video_url: string | null;
  image_url: string | null;
  suggested_rest_seconds: number | null;
  user_id: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutPlan {
  id: string;
  name: string;
  description: string | null;
  user_id: string;
  autoreg_mode: string | null;
  position: number;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutPlanExercise {
  id: string;
  plan_id: string;
  exercise_id: string;
  sequence: number;
  target_sets: number | null;
  target_reps: number | null;
  target_rpe: number | null;
  is_autoreg_exempt: boolean;
  rest_seconds: number | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutSession {
  id: string;
  user_id: string;
  plan_id: string | null;
  started_at: string;
  completed_at: string | null;
  autoreg_mode: string | null;
  recovery_score: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutLogEntry {
  id: string;
  session_id: string;
  exercise_id: string;
  set_number: number;
  weight: number;
  reps: number;
  rpe: number | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Insight {
  id: string;
  user_id: string;
  query_date: string;
  content: string;
  model_used: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  is_read: boolean;
  category: string;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface DashboardWidget {
  id: string;
  user_id: string;
  widget_type: string;
  metric_code?: string | null;
  position: number;
  size: string;
  config_json: string;
  is_visible: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface SharingRelationship {
  id: string;
  owner_id: string;
  grantee_handle: string;
  metric_code: string;
  aggregation_level: string;
  expiration_date: string | null;
  status: string;
  api_token_hash: string | null;
  created_at: string;
  updated_at: string | null;
  last_sync_at: string | null;
  deleted_at: string | null;
}

export interface LeaderboardGroup {
  id: string;
  name: string;
  creator_id: string;
  metric_type_code: string;
  time_frame: string;
  start_date: string | null;
  end_date: string | null;
  invite_code: string;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface LeaderboardMember {
  id: string;
  group_id: string;
  user_handle: string;
  status: string;
  joined_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface ShareRecipient {
  id: string;
  user_id: string;
  name: string;
  public_key: string;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface AsymmetricShare {
  id: string;
  user_id: string;
  recipient_id: string;
  encrypted_data: string;
  encrypted_key: string;
  created_at: string;
  expires_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string | null;
  display_name: string | null;
  theme: string;
  locale: string;
  onboarding_dismissed: boolean;
  is_admin: boolean;
  is_active: boolean;
  created_at: string | null;
}

export interface AdminUser {
  id: string;
  username: string;
  email: string | null;
  display_name: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string | null;
  measurement_count: number;
  goal_count: number;
}

export interface AdminStats {
  key: string;
  total_users: number;
  total_measurements: number;
  total_metric_types: number;
  total_goals: number;
  db_size: string | null;
}

export interface SystemConfigItem {
  key: string;
  value: string;
  description: string;
  category: string;
  is_secret: boolean;
  is_env_override: boolean;
  db_has_value: boolean;
}

export interface CommunityActivity {
  id: string;
  friend_name: string;
  activity_type: string;
  activity_description: string;
  time: string | null;
  value?: number;
  notes?: string;
}

export interface FederatedAccessLog {
  id: string;
  owner_id: string;
  requester_handle: string;
  data_type: string;
  target_date: string;
  accessed_at: string;
}

export interface ApiToken {
  id: string;
  token_hash: string;
  token_prefix: string;
  label: string;
  scopes: string;
  user_id: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
}

export interface Habit {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  color: string;
  icon: string;
  frequency: string;
  target_count: number;
  days_bitmask: number | null;
  stack_hint: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  user_id: string;
  log_date: string;
  completed: boolean;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
  deleted_at: string | null;
}

export interface MoodTag {
  code: string;
  label: string;
  emoji: string | null;
  category: string;
  is_system: boolean;
}

export interface MoodEntry {
  id: string;
  user_id: string;
  entry_date: string;
  mood_score: number;
  energy_level: number | null;
  stress_level: number | null;
  tag_codes: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface JournalEntry {
  id: string;
  user_id: string;
  entry_date: string;
  title: string | null;
  content: string;
  mood_score: number | null;
  is_private: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface AchievementDefinition {
  code: string;
  title: string;
  description: string;
  icon: string;
  tier: string;
  category: string;
  condition_type: string;
  condition_config: string;
  is_hidden: boolean;
  sort_order: number;
}

export interface UserAchievement {
  id: string;
  user_id: string;
  achievement_code: string;
  unlocked_at: string;
  progress_current: number | null;
  progress_target: number | null;
  notified: boolean;
}

export interface Medication {
  id: string;
  user_id: string;
  name: string;
  active_ingredient: string | null;
  strength: string | null;
  form: string;
  instructions: string | null;
  color_hex: string;
  icon: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface MedicationSchedule {
  id: string;
  medication_id: string;
  user_id: string;
  dosage: string;
  times: string[];
  days_of_week: number[] | null;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  deleted_at: string | null;
}

export interface MedicationLog {
  id: string;
  medication_id: string;
  user_id: string;
  schedule_id: string | null;
  taken_at: string | null;
  dosage_taken: string | null;
  skipped: boolean;
  notes: string | null;
  created_at: string;
  deleted_at: string | null;
}

export interface MedicationInventory {
  id: string;
  medication_id: string;
  user_id: string;
  initial_count: number;
  remaining_count: number;
  refill_at_count: number;
  prescription_refills: number | null;
  next_refill_date: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}
