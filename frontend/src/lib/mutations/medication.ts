import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';

export async function createMedication(data: {
  name: string;
  active_ingredient?: string;
  strength?: string;
  form?: string;
  instructions?: string;
  color_hex?: string;
  icon?: string;
}) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'medication',
    id: crypto.randomUUID(),
    data
  });
}

export async function updateMedication(
  medicationId: string,
  data: {
    name?: string;
    active_ingredient?: string;
    strength?: string;
    form?: string;
    instructions?: string;
    color_hex?: string;
    icon?: string;
    is_active?: boolean;
  }
) {
  return mutate({
    kind: 'crud',
    op: 'update',
    entity: 'medication',
    id: medicationId,
    data
  });
}

export async function deleteMedication(medicationId: string) {
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'medication',
    id: medicationId,
    data: { id: medicationId }
  });
}

export async function createSchedule(
  medicationId: string,
  data: {
    dosage: string;
    times: string[];
    days_of_week?: number[] | null;
    start_date?: string | null;
    end_date?: string | null;
  }
) {
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'medication_schedule',
    id: crypto.randomUUID(),
    data: { ...data, medication_id: medicationId }
  });
}

export async function deleteSchedule(scheduleId: string) {
  return mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'medication_schedule',
    id: scheduleId,
    data: { id: scheduleId }
  });
}

export async function toggleMedicationLog(
  medicationId: string,
  scheduleId: string | null,
  time: string | null
) {
  if (scheduleId && time) {
    const today = new Date().toISOString().split('T')[0];
    const existing = await db.medication_log
      .where({ schedule_id: scheduleId })
      .filter((l) => {
        if (!l.taken_at) return false;
        const logDate = l.taken_at.split('T')[0];
        const logTime = l.taken_at.split('T')[1].slice(0, 5);
        return logDate === today && logTime === time && !l.deleted_at;
      })
      .first();

    if (existing) {
      return mutate({
        kind: 'crud',
        op: 'delete',
        entity: 'medication_log',
        id: existing.id,
        data: { id: existing.id }
      });
    }
  }

  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'medication_log',
    id,
    data: {
      medication_id: medicationId,
      schedule_id: scheduleId,
      taken_at: now,
      skipped: false
    },
    optimistic: {
      id,
      medication_id: medicationId,
      user_id: '',
      schedule_id: scheduleId,
      taken_at: now,
      dosage_taken: null,
      skipped: false,
      notes: null,
      created_at: now,
      deleted_at: null
    }
  });
}

export async function skipDose(medicationId: string, scheduleId: string, time: string) {
  const today = new Date().toISOString().split('T')[0];
  const takenAt = `${today}T${time}:00`;
  const id = crypto.randomUUID();
  const now = new Date().toISOString();

  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'medication_log',
    id,
    data: {
      medication_id: medicationId,
      schedule_id: scheduleId,
      taken_at: takenAt,
      skipped: true
    },
    optimistic: {
      id,
      medication_id: medicationId,
      user_id: '',
      schedule_id: scheduleId,
      taken_at: takenAt,
      dosage_taken: null,
      skipped: true,
      notes: null,
      created_at: now,
      deleted_at: null
    }
  });
}

export async function updateInventory(
  medicationId: string,
  data: {
    initial_count?: number;
    remaining_count?: number;
    refill_at_count?: number;
    prescription_refills?: number | null;
    next_refill_date?: string | null;
  }
) {
  const existing = await db.medication_inventory
    .where({ medication_id: medicationId })
    .filter((i) => !i.deleted_at)
    .first();

  if (existing) {
    return mutate({
      kind: 'crud',
      op: 'update',
      entity: 'medication_inventory',
      id: existing.id,
      data: { ...data, medication_id: medicationId }
    });
  }

  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'medication_inventory',
    id: crypto.randomUUID(),
    data: { ...data, medication_id: medicationId }
  });
}
