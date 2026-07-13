import { vi } from 'vitest';

export function setOnline(): void {
  vi.stubGlobal('navigator', { onLine: true });
}

export function setOffline(): void {
  vi.stubGlobal('navigator', { onLine: false });
}
