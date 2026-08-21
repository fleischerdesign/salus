import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export interface ProgramSlotInput {
  workout_id: string;
  sequence: number;
  day_of_week: number | null;
  scheduled_date: string | null;
}

export const createProgram = (
  name: string,
  description: string | null,
  progressionScheme: string,
  slots: ProgramSlotInput[]
) => {
  const programId = uuid7();
  return mutate({
    kind: 'command',
    command: 'create_program',
    queueable: true,
    payload: {
      id: programId,
      name,
      description,
      progression_scheme: progressionScheme,
      slots
    },
    optimisticTable: 'program',
    optimisticData: {
      id: programId,
      user_id: SELF_USER_ID,
      name,
      description,
      progression_scheme: progressionScheme,
      position: 0,
      created_at: now(),
      updated_at: null,
      deleted_at: null
    },
    optimisticRows: [
      {
        table: 'program_workout',
        rows: slots.map((slot) => ({
          ...slot,
          id: uuid7(),
          program_id: programId,
          created_at: now(),
          updated_at: null,
          deleted_at: null
        }))
      }
    ],
    responseTable: 'program'
  });
};

export const deleteProgram = async (programId: string) => {
  const slots = await db.program_workout.where('program_id').equals(programId).toArray();

  return mutate({
    kind: 'command',
    command: 'delete_program',
    queueable: true,
    payload: { id: programId },
    optimisticTable: 'program',
    optimisticData: { id: programId, deleted_at: now() },
    optimisticDelete:
      slots.length > 0
        ? [{ table: 'program_workout', ids: slots.map((slot) => slot.id) }]
        : undefined
  });
};

export const activateProgram = (programId: string) =>
  mutate({
    kind: 'command',
    command: 'activate_program',
    queueable: true,
    payload: { id: programId },
    optimisticTable: 'program',
    optimisticData: { id: programId, is_active: true }
  });

export const deactivateProgram = (programId: string) =>
  mutate({
    kind: 'command',
    command: 'deactivate_program',
    queueable: true,
    payload: { id: programId },
    optimisticTable: 'program',
    optimisticData: { id: programId, is_active: false }
  });
