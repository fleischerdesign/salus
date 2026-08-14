import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { seedReferenceData } from '$lib/db/seed';
import { createLabPanel, deleteLabPanel } from '$lib/mutations/lab';
import { startFastingSession, endFastingSession } from '$lib/mutations/fasting';
import { createMeal, deleteMeal } from '$lib/mutations/meal';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';

const { mockSyncEngine, mockConflictStore } = vi.hoisted(() => ({
  mockSyncEngine: {
    enqueueOutbox: vi.fn().mockResolvedValue(undefined),
    flushSingle: vi.fn().mockResolvedValue({ ok: true }),
    flush: vi.fn().mockResolvedValue(undefined),
    retryFailed: vi.fn().mockResolvedValue(undefined),
    resetSessionExpired: vi.fn(),
    status: 'idle' as string,
    queueLength: 0 as number,
    error: null as string | null,
    sessionExpired: false as boolean
  },
  mockConflictStore: {
    enqueue: vi.fn(),
    resolve: vi.fn(),
    current: null,
    hasPending: false
  }
}));

vi.mock('$lib/db/sync-engine.svelte', () => ({
  syncEngine: mockSyncEngine
}));

vi.mock('$stores/conflict.svelte', () => ({
  conflictStore: mockConflictStore
}));

describe('composed-domain optimistic writes (local-first)', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    vi.stubGlobal('navigator', { onLine: true });
    localStorage.setItem('salus_token', 'test-token');
    await seedReferenceData();
  });

  describe('createLabPanel', () => {
    it('persists panel, results and the measurement bridge locally', async () => {
      await createLabPanel({
        collection_date: '2026-08-15',
        lab_name: 'LabCorp',
        results: [
          { metric_code: 'total_cholesterol', value: 250 },
          { metric_code: 'hdl_cholesterol', value: 50 }
        ]
      });

      expect(await db.lab_panel.count()).toBe(1);

      const results = await db.lab_result.toArray();
      expect(results).toHaveLength(2);
      const panel = await db.lab_panel.toArray();
      const panelId = panel[0].id;
      expect(results.every((r) => r.panel_id === panelId)).toBe(true);

      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(2);
      expect(measurements.every((m) => m.source === 'lab')).toBe(true);
      expect(measurements.every((m) => m.external_id !== null)).toBe(true);
    });

    it('computes is_abnormal from the marker reference range', async () => {
      await createLabPanel({
        results: [{ metric_code: 'total_cholesterol', value: 250 }]
      });

      const result = (await db.lab_result.toArray())[0];
      expect(result?.is_abnormal).toBe(true);
    });

    it('uses the same measurement ids in payload and optimistic rows', async () => {
      await createLabPanel({
        results: [{ metric_code: 'total_cholesterol', value: 150 }]
      });

      const result = (await db.lab_result.toArray())[0];
      const measurement = (await db.measurement.toArray())[0];
      expect(measurement?.external_id).toBe(result?.id);
      expect(measurement?.metric_code).toBe('total_cholesterol');
      expect(measurement?.value_numeric).toBe(150);
    });

    it('cleans up results and measurements on delete', async () => {
      await createLabPanel({
        results: [{ metric_code: 'total_cholesterol', value: 180 }]
      });
      const panel = (await db.lab_panel.toArray())[0];
      expect(await db.lab_result.count()).toBe(1);
      expect(await db.measurement.count()).toBe(1);

      await deleteLabPanel(panel!.id);

      expect(await db.lab_panel.count()).toBe(1);
      expect(((await db.lab_panel.toArray())[0])?.deleted_at).not.toBeNull();
      expect(await db.lab_result.count()).toBe(0);
      expect(await db.measurement.count()).toBe(0);
    });
  });

  describe('fasting session', () => {
    it('writes the fasting_hours measurement on end', async () => {
      const id = uuid7();
      const startedAt = new Date(Date.now() - 2 * 3_600_000).toISOString();
      await db.fasting_session.bulkPut([
        {
          id,
          user_id: SELF_USER_ID,
          started_at: startedAt,
          ended_at: null,
          target_hours: 16,
          fasting_type: 'intermittent',
          water_only: true,
          notes: null,
          mood_during: null,
          difficulty: null,
          created_at: startedAt,
          updated_at: null,
          deleted_at: null
        }
      ]);

      await endFastingSession(id);

      const ended = (await db.fasting_session.toArray())[0];
      expect(ended?.ended_at).not.toBeNull();

      const measurement = (await db.measurement.toArray())[0];
      expect(measurement?.metric_code).toBe('fasting_hours');
      expect(measurement?.external_id).toBe(id);
      expect(measurement?.value_numeric).toBeGreaterThan(1.9);
      expect(measurement?.value_numeric).toBeLessThan(2.1);
    });

    it('does not duplicate the measurement when ended twice', async () => {
      await startFastingSession({});
      const session = (await db.fasting_session.toArray())[0];
      await endFastingSession(session!.id);
      await endFastingSession(session!.id);

      const measurements = await db.measurement
        .where('external_id')
        .equals(session!.id)
        .toArray();
      expect(measurements).toHaveLength(1);
    });
  });

  describe('createMeal', () => {
    it('persists the meal and its items locally', async () => {
      await createMeal({
        meal_type: 'lunch',
        name: 'Salad',
        items: [
          { food_item_id: 'food-1', servings: 1 },
          { food_item_id: 'food-2', servings: 2 }
        ]
      });

      expect(await db.meal.count()).toBe(1);
      const meal = (await db.meal.toArray())[0];
      const items = await db.meal_item.toArray();
      expect(items).toHaveLength(2);
      expect(items.every((i) => i.meal_id === meal!.id)).toBe(true);
    });

    it('removes items when the meal is deleted', async () => {
      await createMeal({ items: [{ food_item_id: 'food-1', servings: 1 }] });
      const meal = (await db.meal.toArray())[0];

      await deleteMeal(meal!.id);

      expect(await db.meal.count()).toBe(0);
      expect(await db.meal_item.count()).toBe(0);
    });
  });
});
