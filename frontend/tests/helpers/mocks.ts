import { vi } from 'vitest';

export function createSyncEngineMock() {
  return {
    enqueue: vi.fn().mockResolvedValue(undefined),
    enqueueDomain: vi.fn().mockResolvedValue(undefined),
    flush: vi.fn().mockResolvedValue(undefined),
    retryFailed: vi.fn().mockResolvedValue(undefined),
    resetSessionExpired: vi.fn(),
    status: 'idle' as string,
    queueLength: 0 as number,
    error: null as string | null,
    sessionExpired: false as boolean
  };
}

export function createConflictStoreMock() {
  return {
    enqueue: vi.fn(),
    resolve: vi.fn(),
    current: null,
    hasPending: false
  };
}
