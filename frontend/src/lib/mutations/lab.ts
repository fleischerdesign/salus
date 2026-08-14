import { mutate } from '$lib/mutate';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { nowIso, todayString } from '$lib/utils/datetime';

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

export function createLabPanel(data: LabPanelInput) {
  const panelId = uuid7();
  const now = nowIso();
  const collectionDate = data.collection_date ?? todayString();
  const results = data.results.map((r) => ({ id: uuid7(), ...r }));

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
        metric_code: r.metric_code,
        value: r.value,
        unit: r.unit ?? null,
        is_abnormal: r.is_abnormal ?? null,
        reference_low: r.reference_low ?? null,
        reference_high: r.reference_high ?? null
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
    responseTable: 'lab_panel'
  });
}

export function deleteLabPanel(panelId: string) {
  return mutate({
    kind: 'command',
    command: 'delete_lab_panel',
    queueable: true,
    payload: { id: panelId },
    optimisticTable: 'lab_panel',
    optimisticData: { id: panelId, deleted_at: nowIso() }
  });
}
