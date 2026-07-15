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

export interface MetricType {
  id: string;
  name: string;
  unit: string;
  data_type: string;
  color: string;
  user_id: string;
  is_system: boolean;
  source_data_type: string | null;
  icon: string;
  widget_size: string;
  widget_enabled: boolean;
  position: number;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Measurement {
  id: string;
  user_id: string;
  metric_type_id: string;
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
  metric_type_id: string;
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
  metric_type_id: string;
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
  metric_type_id: string;
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

