import Dexie, { type EntityTable } from 'dexie';
import type {
  OutboxOp,
  SyncMeta,
  MetricDefinition,
  MetricGroup,
  UserMetricPreference,
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
  Habit,
  HabitLog,
  MoodTag,
  MoodEntry,
  JournalEntry,
  AchievementDefinition,
  UserAchievement,
  Medication,
  MedicationSchedule,
  MedicationLog,
  MedicationInventory,
  FoodItem,
  Meal,
  MealItem,
  Recipe,
  RecipeIngredient
} from './types';

export class SalusDB extends Dexie {
  metric_group!: EntityTable<MetricGroup, 'key'>;
  metric_definition!: EntityTable<MetricDefinition, 'code'>;
  user_metric_preference!: EntityTable<UserMetricPreference, 'id'>;
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
  habit!: EntityTable<Habit, 'id'>;
  habit_log!: EntityTable<HabitLog, 'id'>;
  mood_tag!: EntityTable<MoodTag, 'code'>;
  mood_entry!: EntityTable<MoodEntry, 'id'>;
  journal_entry!: EntityTable<JournalEntry, 'id'>;
  achievement_definition!: EntityTable<AchievementDefinition, 'code'>;
  user_achievement!: EntityTable<UserAchievement, 'id'>;
  medication!: EntityTable<Medication, 'id'>;
  medication_schedule!: EntityTable<MedicationSchedule, 'id'>;
  medication_log!: EntityTable<MedicationLog, 'id'>;
  medication_inventory!: EntityTable<MedicationInventory, 'id'>;
  food_item!: EntityTable<FoodItem, 'id'>;
  meal!: EntityTable<Meal, 'id'>;
  meal_item!: EntityTable<MealItem, 'id'>;
  recipe!: EntityTable<Recipe, 'id'>;
  recipe_ingredient!: EntityTable<RecipeIngredient, 'id'>;
  outbox!: EntityTable<OutboxOp, 'id'>;
  meta!: EntityTable<SyncMeta, 'key'>;
  analytics_cache!: EntityTable<
    { key: string; payload: unknown; computedAt: number; inputHash: number },
    'key'
  >;

  constructor() {
    super('salus');
    this.version(3).stores({
      metric_definition: 'id, user_id, name, is_system',
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
    this.version(10).stores({
      metric_definition: 'code, name',
      measurement: 'id, user_id, metric_code, start_time',
      goal: 'id, user_id, metric_code',
      dashboard_widget: 'id, user_id, metric_code, widget_type'
    });
    this.version(11).stores({
      user_metric_preference: 'id, user_id, metric_code'
    });
    this.version(12).stores({
      metric_group: '&key'
    });
    this.version(13).stores({
      habit: 'id, user_id',
      habit_log: 'id, habit_id, user_id, log_date',
      mood_tag: '&code',
      mood_entry: 'id, user_id',
      journal_entry: 'id, user_id, entry_date',
      achievement_definition: '&code',
      user_achievement: 'id, user_id, achievement_code'
    });
    this.version(14).stores({
      medication: 'id, user_id',
      medication_schedule: 'id, medication_id, user_id',
      medication_log: 'id, medication_id, user_id',
      medication_inventory: 'id, medication_id, user_id'
    });
    this.version(16).stores({
      food_item: 'id, barcode',
      meal: 'id, user_id, log_date',
      meal_item: 'id, meal_id, user_id, food_item_id',
      recipe: 'id, user_id',
      recipe_ingredient: 'id, recipe_id, user_id, food_item_id'
    });
  }
}

export const db = new SalusDB();
