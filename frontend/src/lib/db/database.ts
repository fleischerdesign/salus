import Dexie, { type EntityTable } from 'dexie';
import type {
  QueueOp,
  SyncMeta,
  MetricType,
  Measurement,
  Goal,
  CircadianProfile,
  Exercise,
  WorkoutPlan,
  WorkoutPlanExercise,
  WorkoutSession,
  WorkoutLogEntry,
  Insight,
  Notification,
  DashboardWidget,
  SharingRelationship,
  LeaderboardGroup,
  LeaderboardMember,
  ShareRecipient,
  AsymmetricShare,
  UserProfile,
  AdminUser,
  AdminStats,
  SystemConfigItem,
  ApiToken,
  CommunityActivity,
  FederatedAccessLog,
  DomainQueueOp,
} from './types';

export class SalusDB extends Dexie {
  metric_type!: EntityTable<MetricType, 'id'>;
  measurement!: EntityTable<Measurement, 'id'>;
  goal!: EntityTable<Goal, 'id'>;
  circadian_profile!: EntityTable<CircadianProfile, 'id'>;
  exercise!: EntityTable<Exercise, 'id'>;
  workout_plan!: EntityTable<WorkoutPlan, 'id'>;
  workout_plan_exercise!: EntityTable<WorkoutPlanExercise, 'id'>;
  workout_session!: EntityTable<WorkoutSession, 'id'>;
  workout_log_entry!: EntityTable<WorkoutLogEntry, 'id'>;
  insight!: EntityTable<Insight, 'id'>;
  notification!: EntityTable<Notification, 'id'>;
  dashboard_widget!: EntityTable<DashboardWidget, 'id'>;
  sharing_relationship!: EntityTable<SharingRelationship, 'id'>;
  leaderboard_group!: EntityTable<LeaderboardGroup, 'id'>;
  leaderboard_member!: EntityTable<LeaderboardMember, 'id'>;
  share_recipient!: EntityTable<ShareRecipient, 'id'>;
  asymmetric_share!: EntityTable<AsymmetricShare, 'id'>;
  user_profile!: EntityTable<UserProfile, 'id'>;
  admin_user!: EntityTable<AdminUser, 'id'>;
  admin_stats!: EntityTable<AdminStats, 'key'>;
  system_config!: EntityTable<SystemConfigItem, 'key'>;
  api_token!: EntityTable<ApiToken, 'id'>;
  user!: EntityTable<UserProfile, 'id'>;
  community_activity!: EntityTable<CommunityActivity, 'id'>;
  federated_access_log!: EntityTable<FederatedAccessLog, 'id'>;
  queue!: EntityTable<QueueOp, 'id'>;
  domainQueue!: EntityTable<DomainQueueOp, 'id'>;
  meta!: EntityTable<SyncMeta, 'key'>;

  constructor() {
    super('salus');
    this.version(3).stores({
      metric_type: 'id, user_id, name, is_system',
      measurement: 'id, user_id, metric_type_id, start_time',
      goal: 'id, user_id, metric_type_id',
      circadian_profile: 'id, user_id',
      exercise: 'id, user_id, name',
      workout_plan: 'id, user_id',
      workout_plan_exercise: 'id, plan_id, exercise_id',
      workout_session: 'id, user_id, plan_id, started_at',
      workout_log_entry: 'id, session_id, exercise_id, set_number',
      insight: 'id, user_id, query_date',
      notification: 'id, user_id',
      dashboard_widget: 'id, user_id, metric_type_id',
      sharing_relationship: 'id, owner_id, status',
      leaderboard_group: 'id, creator_id',
      leaderboard_member: 'id, group_id, status',
      share_recipient: 'id, user_id',
      asymmetric_share: 'id, user_id, recipient_id',
      queue: '++id, createdAt',
      meta: '&key',
    });
    this.version(4).stores({
      goal: 'id, user_id, metric_type_id',
      notification: 'id, user_id',
      user_profile: 'id',
      admin_user: 'id',
      admin_stats: '&key',
      system_config: '&key',
      domainQueue: '++id, createdAt',
    });
    this.version(5).stores({
      api_token: 'id, user_id',
      user: 'id',
    });
    this.version(6).stores({
      community_activity: 'id',
      federated_access_log: 'id, owner_id',
    });
  }
}

export const db = new SalusDB();
