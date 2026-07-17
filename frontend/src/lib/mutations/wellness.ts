import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';

export async function createHabit(data: {
  name: string;
  description?: string;
  color: string;
  icon: string;
  frequency: string;
  target_count: number;
  days_bitmask?: number | null;
  stack_hint?: string;
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'habit',
    id: crypto.randomUUID(),
    data
  });
}

export async function toggleHabit(habitId: string) {
  const today = new Date().toISOString().split('T')[0];
  const existing = await db.habit_log
    .where({ habit_id: habitId })
    .filter((l) => l.log_date === today && l.completed)
    .first();

  if (existing) {
    return mutate({
      kind: 'crud',
      op: 'delete',
      entity: 'habit_log',
      id: existing.id,
      data: { id: existing.id }
    });
  }

  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'habit_log',
    id,
    data: {
      habit_id: habitId,
      log_date: today,
      completed: true,
      completed_at: now,
    },
    optimistic: {
      id,
      habit_id: habitId,
      user_id: '',
      log_date: today,
      completed: true,
      completed_at: now,
      notes: null,
      created_at: now,
      deleted_at: null,
    }
  });
}

export async function updateHabit(
  habitId: string,
  data: {
    name?: string;
    description?: string;
    color?: string;
    icon?: string;
    frequency?: string;
    target_count?: number;
    days_bitmask?: number | null;
    stack_hint?: string;
    is_archived?: boolean;
  }
) {
  return mutate({
    kind: 'crud',
    op: 'update',
    entity: 'habit',
    id: habitId,
    data
  });
}

export async function deleteHabit(habitId: string) {
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'habit',
    id: habitId,
    data: { id: habitId }
  });
}

export async function createMoodEntry(data: {
  entry_date?: string;
  mood_score: number;
  energy_level?: number | null;
  stress_level?: number | null;
  tag_codes?: string[] | null;
  notes?: string | null;
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'mood_entry',
    id: crypto.randomUUID(),
    data
  });
}

export async function createJournalEntry(data: {
  entry_date?: string;
  title?: string;
  content: string;
  mood_score?: number | null;
  is_private?: boolean;
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'journal_entry',
    id: crypto.randomUUID(),
    data
  });
}
