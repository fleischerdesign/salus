import { describe, expect, it, vi } from 'vitest';

const { mutateMock } = vi.hoisted(() => ({ mutateMock: vi.fn() }));

vi.mock('$lib/mutate', () => ({ mutate: mutateMock }));

import { logSet, startWorkout } from '$lib/mutations/workout';

describe('workout command mutations', () => {
  it('startWorkout uses a single id for payload and optimisticData', async () => {
    mutateMock.mockResolvedValueOnce({ ok: true, queued: true });

    await startWorkout('plan-1');

    const mutation = mutateMock.mock.calls[0][0];
    expect(mutation.payload.id).toBe(mutation.optimisticData.id);
  });

  it('logSet uses a single id for payload and optimisticData', async () => {
    mutateMock.mockResolvedValueOnce({ ok: true, queued: true });

    await logSet('session-1', 'exercise-1', 1, 100, 5);

    const mutation = mutateMock.mock.calls[0][0];
    expect(mutation.payload.id).toBe(mutation.optimisticData.id);
  });
});
