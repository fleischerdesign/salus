import { db } from './database';
import { pullFull, pullDelta } from './sync-pull';
import { fetchEntityNames } from './entity-info';

const DELTA_MAX_AGE_MS = 7 * 24 * 3600 * 1000;

export const offlineService = {
  async syncAll(
    onProgress?: (message: string) => void,
  ): Promise<boolean | 'unauthorized'> {
    if (typeof navigator !== 'undefined' && !navigator.onLine) return false;

    await fetchEntityNames();

    const last = await db.meta.get('lastSyncAt');
    const lastSync = (last?.value as number) ?? 0;
    const useDelta = lastSync > 0 && (Date.now() - lastSync) < DELTA_MAX_AGE_MS;

    if (useDelta) {
      const deltaResult = await pullDelta(onProgress);
      if (deltaResult === 'unauthorized') return 'unauthorized';
      if (deltaResult) return true;
    }

    return pullFull(onProgress);
  },
};
