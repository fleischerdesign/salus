import { mutate } from '$lib/mutate';

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
  const res = await fetch(`/api/v1/habits/${habitId}/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  return res.json();
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
