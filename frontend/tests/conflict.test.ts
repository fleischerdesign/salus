import { describe, it, expect } from 'vitest';
import { conflictStore } from '$stores/conflict.svelte';

describe('conflictStore', () => {
  it('starts empty', () => {
    expect(conflictStore.current).toBe(null);
    expect(conflictStore.hasPending).toBe(false);
  });

  it('enqueue adds conflict', () => {
    const c = {
      id: crypto.randomUUID(),
      table: 'goal',
      clientRecord: { name: 'X', target_value: 100 },
      serverRecord: { name: 'X', target_value: 50 },
    };
    conflictStore.enqueue(c);
    expect(conflictStore.hasPending).toBe(true);
    expect(conflictStore.current?.id).toBe(c.id);
    expect(conflictStore.current?.table).toBe('goal');
    conflictStore.resolve(c.id);
  });

  it('resolve removes conflict', () => {
    const c1 = { id: crypto.randomUUID(), table: 'goal', clientRecord: {}, serverRecord: {} };
    conflictStore.enqueue(c1);
    conflictStore.resolve(c1.id);
    expect(conflictStore.current).toBe(null);
    expect(conflictStore.hasPending).toBe(false);
  });

  it('respects FIFO order', () => {
    const c1 = { id: crypto.randomUUID(), table: 'goal', clientRecord: {}, serverRecord: {} };
    const c2 = { id: crypto.randomUUID(), table: 'measurement', clientRecord: {}, serverRecord: {} };
    conflictStore.enqueue(c1);
    conflictStore.enqueue(c2);
    expect(conflictStore.current?.id).toBe(c1.id);

    conflictStore.resolve(c1.id);
    expect(conflictStore.current?.id).toBe(c2.id);

    conflictStore.resolve(c2.id);
    expect(conflictStore.current).toBe(null);
  });

  it('resolve non-existent is no-op', () => {
    const c = { id: crypto.randomUUID(), table: 'goal', clientRecord: {}, serverRecord: {} };
    conflictStore.enqueue(c);
    conflictStore.resolve('nonexistent');
    expect(conflictStore.current?.id).toBe(c.id);
    conflictStore.resolve(c.id);
  });
});
