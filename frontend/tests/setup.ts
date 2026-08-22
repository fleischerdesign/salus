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

// jsdom does not implement matchMedia; the theme store's reactive
// prefers-color-scheme MediaQuery depends on it (node env has no window).
if (typeof window !== 'undefined' && typeof window.matchMedia !== 'function') {
  vi.stubGlobal(
    'matchMedia',
    vi.fn((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    }))
  );
}

if (!globalThis.crypto?.randomUUID) {
  vi.stubGlobal('crypto', {
    ...globalThis.crypto,
    randomUUID: () => `test-uuid-${Math.random().toString(36).slice(2)}`
  });
}
