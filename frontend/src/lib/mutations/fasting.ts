import { mutate } from '$lib/mutate';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { nowIso } from '$lib/utils/datetime';

export function startFastingSession(data: {
  target_hours?: number;
  fasting_type?: string;
  water_only?: boolean;
}) {
  const id = uuid7();
  const now = nowIso();
  return mutate({
    kind: 'command',
    command: 'start_fasting_session',
    queueable: true,
    payload: {
      id,
      target_hours: data.target_hours ?? 16,
      fasting_type: data.fasting_type ?? 'intermittent',
      water_only: data.water_only ?? true
    },
    optimisticTable: 'fasting_session',
    optimisticData: {
      id,
      user_id: SELF_USER_ID,
      started_at: now,
      ended_at: null,
      target_hours: data.target_hours ?? 16,
      fasting_type: data.fasting_type ?? 'intermittent',
      water_only: data.water_only ?? true,
      notes: null,
      mood_during: null,
      difficulty: null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    },
    responseTable: 'fasting_session'
  });
}

export function endFastingSession(sessionId: string) {
  return mutate({
    kind: 'command',
    command: 'end_fasting_session',
    queueable: true,
    payload: { session_id: sessionId },
    optimisticTable: 'fasting_session',
    optimisticData: { id: sessionId, ended_at: nowIso() }
  });
}

export function cancelFastingSession(sessionId: string) {
  return mutate({
    kind: 'command',
    command: 'cancel_fasting_session',
    queueable: true,
    payload: { session_id: sessionId },
    optimisticTable: 'fasting_session',
    optimisticData: { id: sessionId, deleted_at: nowIso() }
  });
}

export function deleteFastingSession(sessionId: string) {
  return mutate({
    kind: 'command',
    command: 'delete_fasting_session',
    queueable: true,
    payload: { session_id: sessionId },
    optimisticTable: 'fasting_session',
    optimisticData: { id: sessionId, deleted_at: nowIso() }
  });
}
