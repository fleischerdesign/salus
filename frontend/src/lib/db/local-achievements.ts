import { db } from './database';
import type { AchievementDefinition } from './types';

interface HabitLogLike {
  completed: boolean;
  log_date: string;
  deleted_at?: string | null;
}

interface MoodEntryLike {
  entry_date: string;
  deleted_at?: string | null;
}

interface WorkoutSessionLike {
  completed_at: string | null;
  deleted_at?: string | null;
}

interface AchievementContext {
  measurementCount: number;
  measurementDays: string[];
  measurementHourCounts: number[];
  habitCount: number;
  habitLogs: HabitLogLike[];
  moodEntries: MoodEntryLike[];
  goalCount: number;
  workoutSessions: WorkoutSessionLike[];
}

interface ConditionConfig {
  entity?: string;
  op?: string;
  value?: number;
  days?: number;
  hour_before?: number;
  hour_after?: number;
  within_days?: number;
  conditions?: ConditionConfig[];
  type?: string;
}

function dayKey(iso: string): string {
  return iso.slice(0, 10);
}

function prevDay(d: string): string {
  const [year, month, day] = d.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day - 1)).toISOString().slice(0, 10);
}

function longestStreak(dates: string[]): number {
  const unique = [...new Set(dates.map(dayKey))].sort().reverse();
  if (unique.length === 0) return 0;

  let longest = 1;
  let run = 1;
  for (let i = 1; i < unique.length; i++) {
    run = prevDay(unique[i - 1]) === unique[i] ? run + 1 : 1;
    if (run > longest) longest = run;
  }
  return longest;
}

function countEntity(
  ctx: AchievementContext,
  entity: string,
  op: string,
  value: number,
  config: ConditionConfig
): boolean {
  let count = 0;
  switch (entity) {
    case 'measurement':
      if (config.hour_before !== undefined || config.hour_after !== undefined) {
        const after = config.hour_after ?? 0;
        const before = config.hour_before ?? 24;
        count = ctx.measurementHourCounts.reduce(
          (acc, n, hour) => (hour >= after && hour < before ? acc + n : acc),
          0
        );
      } else {
        count = ctx.measurementCount;
      }
      break;
    case 'habit':
      count = ctx.habitCount;
      break;
    case 'habit_log':
      count = ctx.habitLogs.filter((l) => l.completed).length;
      break;
    case 'mood_entry':
      count = ctx.moodEntries.length;
      break;
    case 'goal':
      count = ctx.goalCount;
      break;
    case 'workout_session':
      count = ctx.workoutSessions.filter((s) => {
        if (!s.completed_at) return false;
        if (config.within_days !== undefined) {
          const since = Date.now() - config.within_days * 86400000;
          if (new Date(s.completed_at).getTime() < since) return false;
        }
        return true;
      }).length;
      break;
    case 'sharing_relationship':
    case 'open_science_consent':
      count = 0;
      break;
    default:
      return false;
  }

  switch (op) {
    case 'gte':
      return count >= value;
    case 'gt':
      return count > value;
    case 'eq':
      return count === value;
    default:
      return false;
  }
}

function streakEntity(ctx: AchievementContext, entity: string, days: number): boolean {
  switch (entity) {
    case 'measurement':
      return longestStreak(ctx.measurementDays) >= days;
    case 'habit_log':
      return longestStreak(ctx.habitLogs.filter((l) => l.completed).map((l) => l.log_date)) >= days;
    case 'mood_entry':
      return longestStreak(ctx.moodEntries.map((m) => m.entry_date)) >= days;
    default:
      return false;
  }
}

function evaluateCondition(ctx: AchievementContext, condition: ConditionConfig): boolean {
  if (condition.type === 'streak') {
    return streakEntity(ctx, condition.entity ?? '', Number(condition.days ?? 7));
  }
  return countEntity(
    ctx,
    condition.entity ?? '',
    condition.op ?? 'gte',
    Number(condition.value ?? 1),
    condition
  );
}

function evaluateAchievement(ctx: AchievementContext, definition: AchievementDefinition): boolean {
  let config: ConditionConfig;
  try {
    config = JSON.parse(definition.condition_config);
  } catch {
    return false;
  }

  switch (definition.condition_type) {
    case 'count':
      return countEntity(
        ctx,
        config.entity ?? '',
        config.op ?? 'gte',
        Number(config.value ?? 1),
        config
      );
    case 'streak':
      return streakEntity(ctx, config.entity ?? '', Number(config.days ?? 7));
    case 'compound': {
      const conditions = config.conditions ?? [];
      if (conditions.length === 0) return false;
      const results = conditions.map((c) => evaluateCondition(ctx, c));
      return config.op === 'or' ? results.some(Boolean) : results.every(Boolean);
    }
    default:
      return false;
  }
}

/**
 * Streams the measurement aggregates needed by the local evaluator in a single
 * in-flight pass — no full array is materialized (bounded memory for large
 * datasets): total count, per-UTC-hour buckets and the distinct measurement days.
 */
async function aggregateMeasurements(): Promise<{
  count: number;
  days: string[];
  hourCounts: number[];
}> {
  let count = 0;
  const days = new Set<string>();
  const hourCounts = new Array<number>(24).fill(0);
  await db.measurement.each((m) => {
    if (m.deleted_at) return;
    count++;
    hourCounts[new Date(m.start_time).getUTCHours()]++;
    days.add(m.start_time.slice(0, 10));
  });
  return { count, days: [...days], hourCounts };
}

/**
 * Computes the set of locally-unlocked achievement codes from Dexie. Mirrors the
 * server-side evaluator (services/achievement/evaluator.py); server-only
 * conditions (sharing_relationship, open_science_consent) never unlock locally.
 */
export async function evaluateLocalAchievements(): Promise<Set<string>> {
  const [definitions, measurementAgg, habits, habitLogs, moodEntries, goals, workoutSessions] =
    await Promise.all([
      db.achievement_definition.toArray(),
      aggregateMeasurements(),
      db.habit.toArray(),
      db.habit_log.toArray(),
      db.mood_entry.toArray(),
      db.goal.toArray(),
      db.workout_session.toArray()
    ]);

  const ctx: AchievementContext = {
    measurementCount: measurementAgg.count,
    measurementDays: measurementAgg.days,
    measurementHourCounts: measurementAgg.hourCounts,
    habitCount: habits.filter((h) => !h.deleted_at).length,
    habitLogs: habitLogs.filter((l) => !l.deleted_at),
    moodEntries: moodEntries.filter((m) => !m.deleted_at),
    goalCount: goals.filter((g) => !g.deleted_at).length,
    workoutSessions: workoutSessions.filter((s) => !s.deleted_at)
  };

  const unlocked = new Set<string>();
  for (const definition of definitions) {
    if (evaluateAchievement(ctx, definition)) {
      unlocked.add(definition.code);
    }
  }
  return unlocked;
}
