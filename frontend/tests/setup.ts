import 'fake-indexeddb/auto';
import { vi } from 'vitest';

const _store: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (k: string) => _store[k] ?? null,
  setItem: (k: string, v: string) => {
    _store[k] = v;
  },
  removeItem: (k: string) => {
    delete _store[k];
  },
  clear: () => {
    for (const k of Object.keys(_store)) delete _store[k];
  }
});

vi.stubGlobal('navigator', { onLine: true });

if (!globalThis.crypto?.randomUUID) {
  vi.stubGlobal('crypto', {
    ...globalThis.crypto,
    randomUUID: () => `test-uuid-${Math.random().toString(36).slice(2)}`
  });
}
