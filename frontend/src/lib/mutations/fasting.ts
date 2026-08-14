import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { nowIso } from '$lib/utils/datetime';

const FASTING_SOURCE = 'fasting';
const FASTING_METRIC_CODE = 'fasting_hours';

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

export async function endFastingSession(sessionId: string) {
  const now = nowIso();
  const session = await db.fasting_session.get(sessionId);
  if (session?.ended_at) {
    return mutate({
      kind: 'command',
      command: 'end_fasting_session',
      queueable: true,
      payload: { session_id: sessionId },
      optimisticTable: 'fasting_session',
      optimisticData: { id: sessionId, ended_at: session.ended_at }
    });
  }

  const startedAt = session?.started_at ?? now;
  const hours =
    Math.round(((new Date(now).getTime() - new Date(startedAt).getTime()) / 3_600_000) * 100) / 100;
  const measurementId = uuid7();

  return mutate({
    kind: 'command',
    command: 'end_fasting_session',
    queueable: true,
    payload: { session_id: sessionId, measurement_id: measurementId, ended_at: now },
    optimisticTable: 'fasting_session',
    optimisticData: { id: sessionId, ended_at: now },
    optimisticRows: [
      {
        table: 'measurement',
        rows: [
          {
            id: measurementId,
            user_id: SELF_USER_ID,
            metric_code: FASTING_METRIC_CODE,
            source_data_type: FASTING_SOURCE,
            source: FASTING_SOURCE,
            value_numeric: hours,
            value_text: null,
            value_json: null,
            start_time: startedAt,
            end_time: now,
            notes: null,
            external_id: sessionId,
            created_at: now,
            updated_at: null,
            deleted_at: null
          }
        ]
      }
    ]
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

export async function deleteFastingSession(sessionId: string) {
  const measurements = await db.measurement.where('external_id').equals(sessionId).toArray();

  return mutate({
    kind: 'command',
    command: 'delete_fasting_session',
    queueable: true,
    payload: { session_id: sessionId },
    optimisticTable: 'fasting_session',
    optimisticData: { id: sessionId, deleted_at: nowIso() },
    optimisticDelete:
      measurements.length > 0
        ? [{ table: 'measurement', ids: measurements.map((m) => m.id) }]
        : undefined
  });
}
