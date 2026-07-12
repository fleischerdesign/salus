export interface QueueOp {
  id?: number;
  type: 'create' | 'update' | 'delete';
  entity: string;
  client_id: string;
  data?: Record<string, unknown>;
  realId?: number;
  expected_updated_at?: string;
  createdAt: number;
  retries: number;
}

export interface SyncMeta {
  key: string;
  value: unknown;
}

export type SyncStatus = 'idle' | 'syncing' | 'error';

export interface MetricType {
  id: number;
  name: string;
  unit: string;
  data_type: string;
  color: string;
  user_id: number;
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
  id: number;
  user_id: number;
  metric_type_id: number;
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
  id: number;
  user_id: number;
  metric_type_id: number;
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
  id: number;
  user_id: number;
  latitude: number;
  longitude: number;
  timezone_offset_hours: number;
  configured_chronotype: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Exercise {
  id: number;
  name: string;
  equipment: string | null;
  primary_muscles: string | null;
  secondary_muscles: string | null;
  description: string | null;
  instructions: string | null;
  video_url: string | null;
  image_url: string | null;
  suggested_rest_seconds: number | null;
  user_id: number | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutPlan {
  id: number;
  name: string;
  description: string | null;
  user_id: number;
  autoreg_mode: string | null;
  position: number;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface WorkoutPlanExercise {
  id: number;
  plan_id: number;
  exercise_id: number;
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
  id: number;
  user_id: number;
  plan_id: number | null;
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
  id: number;
  session_id: number;
  exercise_id: number;
  set_number: number;
  weight: number;
  reps: number;
  rpe: number | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Insight {
  id: number;
  user_id: number;
  query_date: string;
  content: string;
  model_used: string | null;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  is_read: boolean;
  category: string;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface DashboardWidget {
  id: number;
  user_id: number;
  metric_type_id: number;
  position: number;
  size: string;
  config_json: string;
  is_visible: boolean;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface SharingRelationship {
  id: number;
  owner_id: number;
  grantee_handle: string;
  metric_type_id: number;
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
  id: number;
  name: string;
  creator_id: number;
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
  id: number;
  group_id: number;
  user_handle: string;
  status: string;
  joined_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface ShareRecipient {
  id: number;
  user_id: number;
  name: string;
  public_key: string;
  created_at: string;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface AsymmetricShare {
  id: number;
  user_id: number;
  recipient_id: number;
  encrypted_data: string;
  encrypted_key: string;
  created_at: string;
  expires_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
}

export interface UserProfile {
  id: number;
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
  id: number;
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
  id: number;
  friend_name: string;
  activity_type: string;
  activity_description: string;
  time: string | null;
  value?: number;
  notes?: string;
}

export interface FederatedAccessLog {
  id: number;
  owner_id: number;
  requester_handle: string;
  data_type: string;
  target_date: string;
  accessed_at: string;
}

export interface ApiToken {
  id: number;
  token_hash: string;
  token_prefix: string;
  label: string;
  scopes: string;
  user_id: number;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
}

export interface DomainQueueOp {
  id?: number;
  url: string;
  method: string;
  body?: Record<string, unknown>;
  responseTable?: string;
  retries?: number;
  createdAt: string;
}
