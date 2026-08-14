import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { nowIso, todayString } from '$lib/utils/datetime';
import { startOfLocalDayMs, userTimezone } from '$lib/utils/timezone';

const LAB_SOURCE = 'lab';

export interface LabResultInput {
  metric_code: string;
  value: number;
  unit?: string;
  is_abnormal?: boolean;
  reference_low?: number;
  reference_high?: number;
}

export interface LabPanelInput {
  collection_date?: string;
  lab_name?: string | null;
  fasting?: boolean;
  notes?: string | null;
  results: LabResultInput[];
}

function outOfRange(value: number, low: number | null, high: number | null): boolean {
  if (low != null && value < low) return true;
  if (high != null && value > high) return true;
  return false;
}

export async function createLabPanel(data: LabPanelInput) {
  const panelId = uuid7();
  const now = nowIso();
  const collectionDate = data.collection_date ?? todayString();
  const startTime = new Date(startOfLocalDayMs(collectionDate, userTimezone())).toISOString();

  const markers = await db.lab_marker.toArray();
  const markerByCode = new Map(markers.map((m) => [m.code, m]));

  const results = data.results.map((r) => {
    const marker = markerByCode.get(r.metric_code);
    const referenceLow = r.reference_low ?? marker?.reference_low ?? null;
    const referenceHigh = r.reference_high ?? marker?.reference_high ?? null;
    const value = Number(r.value);
    return {
      id: uuid7(),
      measurement_id: uuid7(),
      metric_code: r.metric_code,
      value,
      unit: r.unit ?? null,
      is_abnormal: r.is_abnormal ?? outOfRange(value, referenceLow, referenceHigh),
      reference_low: referenceLow,
      reference_high: referenceHigh
    };
  });

  return mutate({
    kind: 'command',
    command: 'create_lab_panel',
    queueable: true,
    payload: {
      id: panelId,
      collection_date: collectionDate,
      lab_name: data.lab_name ?? null,
      fasting: data.fasting ?? false,
      notes: data.notes ?? null,
      results: results.map((r) => ({
        id: r.id,
        measurement_id: r.measurement_id,
        metric_code: r.metric_code,
        value: r.value,
        unit: r.unit,
        is_abnormal: r.is_abnormal,
        reference_low: r.reference_low,
        reference_high: r.reference_high
      }))
    },
    optimisticTable: 'lab_panel',
    optimisticData: {
      id: panelId,
      user_id: SELF_USER_ID,
      collection_date: collectionDate,
      lab_name: data.lab_name ?? null,
      fasting: data.fasting ?? false,
      notes: data.notes ?? null,
      attachment_path: null,
      created_at: now,
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'lab_result',
        rows: results.map((r) => ({
          id: r.id,
          panel_id: panelId,
          user_id: SELF_USER_ID,
          metric_code: r.metric_code,
          value: r.value,
          unit: r.unit,
          is_abnormal: r.is_abnormal,
          reference_low: r.reference_low,
          reference_high: r.reference_high,
          created_at: now,
          updated_at: null,
          deleted_at: null
        }))
      },
      {
        table: 'measurement',
        rows: results.map((r) => ({
          id: r.measurement_id,
          user_id: SELF_USER_ID,
          metric_code: r.metric_code,
          source_data_type: LAB_SOURCE,
          source: LAB_SOURCE,
          value_numeric: r.value,
          value_text: null,
          value_json: null,
          start_time: startTime,
          end_time: null,
          notes: null,
          external_id: r.id,
          created_at: now,
          updated_at: null,
          deleted_at: null
        }))
      }
    ],
    responseTable: 'lab_panel'
  });
}

export async function deleteLabPanel(panelId: string) {
  const results = await db.lab_result.where('panel_id').equals(panelId).toArray();
  const resultIds = results.map((r) => r.id);
  const measurements =
    resultIds.length > 0
      ? await db.measurement.where('external_id').anyOf(resultIds).toArray()
      : [];

  return mutate({
    kind: 'command',
    command: 'delete_lab_panel',
    queueable: true,
    payload: { id: panelId },
    optimisticTable: 'lab_panel',
    optimisticData: { id: panelId, deleted_at: nowIso() },
    optimisticDelete: [
      ...(resultIds.length > 0 ? [{ table: 'lab_result', ids: resultIds }] : []),
      ...(measurements.length > 0
        ? [{ table: 'measurement', ids: measurements.map((m) => m.id) }]
        : [])
    ]
  });
}
