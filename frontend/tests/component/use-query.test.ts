import { render, waitFor } from '@testing-library/svelte';
import Dexie from 'dexie';
import { beforeEach, describe, expect, it } from 'vitest';
import Fixture from './use-query-fixture.svelte';

interface HabitRow {
  id?: number;
  name: string;
}

let db: Dexie;

beforeEach(async () => {
  db = new Dexie(`use-query-${Math.random().toString(36).slice(2)}`);
  db.version(1).stores({ habit: '++id, name' });
  await db.open();
});

describe('useQuery', () => {
  it('delivers data and flips loading to false', async () => {
    await db.table<HabitRow>('habit').bulkAdd([{ name: 'a' }, { name: 'b' }]);

    const { container } = render(Fixture, {
      querier: () => db.table<HabitRow>('habit').toArray()
    });

    expect(container.querySelector('.loading')).not.toBeNull();

    await waitFor(() => {
      expect(container.querySelector('.loaded')?.textContent).toBe('loaded:2');
    });
    expect(container.querySelector('.loading')).toBeNull();
  });

  it('re-renders reactively when the underlying table changes', async () => {
    const { container } = render(Fixture, {
      querier: () => db.table<HabitRow>('habit').toArray()
    });

    await waitFor(() => {
      expect(container.textContent).toContain('loaded:0');
    });

    await db.table<HabitRow>('habit').add({ name: 'c' });

    await waitFor(() => {
      expect(container.textContent).toContain('loaded:1');
    });
  });
});
