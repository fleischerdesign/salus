import { db } from './database';
import { uuid7 } from './uuid';
import { SELF_USER_ID } from '$lib/constants';
import reference from '$lib/reference/reference.json';

interface ReferenceMetricGroup {
  key: string;
  name: string;
  icon: string;
  description: string | null;
  input_mode: string;
}

interface ReferenceMetricDefinition {
  code: string;
  name: string;
  unit: string;
  data_type: string;
  source_data_type: string | null;
  group_key: string | null;
  description: string | null;
  sort_order: number;
  min_value: number | null;
  max_value: number | null;
}

interface ReferenceAchievementDefinition {
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

interface ReferenceMoodTag {
  code: string;
  label: string;
  emoji: string | null;
  category: string;
  is_system: boolean;
}

interface ReferenceMetricPreferenceDefault {
  code: string;
  color: string;
  icon: string;
  widget_size: string;
  widget_enabled: boolean;
  enabled: boolean;
  position: number;
}

interface ReferenceLabMarker {
  code: string;
  category: string;
  reference_low: number | null;
  reference_high: number | null;
  optimal_low: number | null;
  optimal_high: number | null;
  description: string | null;
}

interface ReferenceFoodItem {
  id: string;
  name: string;
  serving_size: number;
  calories_per_serving: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number | null;
  sugar_g: number | null;
  saturated_fat_g: number | null;
  sodium_mg: number | null;
}

interface ReferenceExercise {
  id: string;
  name: string;
  equipment: string;
  primary_muscles: string;
  secondary_muscles: string | null;
  description: string | null;
  instructions: string | null;
  suggested_rest_seconds: number;
}

interface ReferenceWorkout {
  id: string;
  name: string;
  description: string | null;
  position: number;
}

interface ReferenceWorkoutExercise {
  id: string;
  workout_id: string;
  exercise_id: string;
  sequence: number;
  target_sets: number;
  target_reps: number;
  target_rpe: number;
  is_autoreg_exempt: boolean;
  rest_seconds: number | null;
}

interface ReferenceProgram {
  id: string;
  name: string;
  description: string | null;
  progression_scheme: string;
  position: number;
  is_active: boolean;
}

interface ReferenceProgramWorkout {
  id: string;
  program_id: string;
  workout_id: string;
  sequence: number;
  day_of_week: number | null;
  scheduled_date: string | null;
}

interface ReferenceData {
  version: number;
  metric_group: ReferenceMetricGroup[];
  metric_definition: ReferenceMetricDefinition[];
  achievement_definition: ReferenceAchievementDefinition[];
  mood_tag: ReferenceMoodTag[];
  lab_marker: ReferenceLabMarker[];
  food_item: ReferenceFoodItem[];
  exercise?: ReferenceExercise[];
  workout?: ReferenceWorkout[];
  workout_exercise?: ReferenceWorkoutExercise[];
  program?: ReferenceProgram[];
  program_workout?: ReferenceProgramWorkout[];
  metric_preference_defaults: ReferenceMetricPreferenceDefault[];
}

const data = reference as ReferenceData;

/**
 * Seeds code-defined reference data into Dexie when the store is empty, so the
 * app renders its metric/achievement structure without a first full sync. A
 * subsequent full sync overwrites it (server is authoritative).
 *
 * Each reference table is seeded independently when it is empty, so tables
 * added after an install's initial seed (e.g. lab markers) still get backfilled.
 */
export async function seedReferenceData(): Promise<void> {
  if ((await db.metric_definition.count()) === 0) {
    await db.metric_group.bulkPut(data.metric_group);
    await db.metric_definition.bulkPut(data.metric_definition);
  }
  if ((await db.achievement_definition.count()) === 0) {
    await db.achievement_definition.bulkPut(data.achievement_definition);
  }
  if ((await db.mood_tag.count()) === 0) {
    await db.mood_tag.bulkPut(data.mood_tag);
  }
  if ((await db.lab_marker.count()) === 0) {
    await db.lab_marker.bulkPut(data.lab_marker);
  }
  if ((await db.food_item.count()) === 0) {
    const now = new Date().toISOString();
    await db.food_item.bulkPut(
      data.food_item.map((f) => ({
        ...f,
        brand: null,
        barcode: null,
        serving_unit: 'g',
        is_verified: true,
        user_id: null,
        source: 'system',
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }
  if (data.exercise && (await db.exercise.count()) === 0) {
    const now = new Date().toISOString();
    await db.exercise.bulkPut(
      data.exercise.map((e) => ({
        ...e,
        video_url: null,
        image_url: null,
        user_id: null,
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }

  if (data.workout && (await db.workout.count()) === 0) {
    const now = new Date().toISOString();
    await db.workout.bulkPut(
      data.workout.map((w) => ({
        ...w,
        user_id: null,
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }

  if (data.workout_exercise && (await db.workout_exercise.count()) === 0) {
    const now = new Date().toISOString();
    await db.workout_exercise.bulkPut(
      data.workout_exercise.map((we) => ({
        ...we,
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }

  if (data.program && (await db.program.count()) === 0) {
    const now = new Date().toISOString();
    await db.program.bulkPut(
      data.program.map((p) => ({
        ...p,
        user_id: null,
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }

  if (data.program_workout && (await db.program_workout.count()) === 0) {
    const now = new Date().toISOString();
    await db.program_workout.bulkPut(
      data.program_workout.map((pw) => ({
        ...pw,
        created_at: now,
        updated_at: null,
        deleted_at: null
      }))
    );
  }

  if ((await db.user_metric_preference.count()) === 0) {
    const preferences = data.metric_preference_defaults.map((p) => ({
      id: uuid7(),
      user_id: SELF_USER_ID,
      metric_code: p.code,
      enabled: p.enabled,
      color: p.color,
      icon: p.icon,
      widget_size: p.widget_size,
      widget_enabled: p.widget_enabled,
      position: p.position
    }));
    await db.user_metric_preference.bulkPut(preferences);
  }
}
