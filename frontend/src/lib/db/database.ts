import Dexie, { type EntityTable } from 'dexie';
import type {
  OutboxOp,
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
  FederatedAccessLog
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
  outbox!: EntityTable<OutboxOp, 'id'>;
  meta!: EntityTable<SyncMeta, 'key'>;
  analytics_cache!: EntityTable<
    { key: string; payload: unknown; computedAt: number; inputHash: number },
    'key'
  >;

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
      meta: '&key'
    });
    this.version(4).stores({
      goal: 'id, user_id, metric_type_id',
      notification: 'id, user_id',
      user_profile: 'id',
      admin_user: 'id',
      admin_stats: '&key',
      system_config: '&key',
      domainQueue: '++id, createdAt'
    });
    this.version(5).stores({
      api_token: 'id, user_id',
      user: 'id'
    });
    this.version(6).stores({
      community_activity: 'id',
      federated_access_log: 'id, owner_id'
    });
    this.version(7)
      .stores({
        queue: null,
        domainQueue: null,
        outbox: '++id, createdAt, kind'
      })
      .upgrade(async (tx) => {
        const oldQueue = await tx
          .table('queue')
          .toArray()
          .catch(() => []);
        const oldDomainQueue = await tx
          .table('domainQueue')
          .toArray()
          .catch(() => []);
        const now = new Date().toISOString();
        const migrated = [
          ...oldQueue.map((item: Record<string, unknown>) => ({
            kind: 'crud' as const,
            opType: item.type as string,
            entity: item.entity as string,
            client_id: item.client_id as string,
            data: item.data as Record<string, unknown> | undefined,
            realId: item.realId as string | undefined,
            expected_updated_at: item.expected_updated_at as string | undefined,
            createdAt: (item.createdAt as number)
              ? new Date(item.createdAt as number).toISOString()
              : now,
            retries: (item.retries as number) ?? 0
          })),
          ...oldDomainQueue.map((item: Record<string, unknown>) => ({
            kind: 'command' as const,
            command: item.url as string,
            client_id: crypto.randomUUID(),
            payload: item.body as Record<string, unknown> | undefined,
            responseTable: item.responseTable as string | undefined,
            createdAt: (item.createdAt as string) ?? now,
            retries: (item.retries as number) ?? 0
          }))
        ];
        if (migrated.length > 0) {
          await tx.table('outbox').bulkPut(migrated);
        }
      });
    this.version(8).stores({
      analytics_cache: '&key'
    });
    this.version(9)
      .stores({
        dashboard_widget: 'id, user_id, metric_type_id, widget_type'
      })
      .upgrade(async (tx) => {
        await tx
          .table('dashboard_widget')
          .toCollection()
          .modify((widget: Record<string, unknown>) => {
            if (!widget.widget_type) {
              widget.widget_type = 'metric';
            }
          });
      });
  }
}

export const db = new SalusDB();
