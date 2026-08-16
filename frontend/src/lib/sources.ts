import { Capacitor } from '@capacitor/core';
import { db } from '$lib/db/database';
import { healthSyncService } from '$lib/native/health-sync.svelte';
import { updateSourceStatus } from '$lib/mutations/source-status';

export interface SourceStatus {
  enabled: boolean;
  reason: 'granted' | 'missing_permissions' | 'not_connected' | 'has_data' | 'always';
  detail?: string;
}

export interface SourceEntry {
  id: string;
  name: string;
  icon: string;
  color: string;
  getStatus(): Promise<SourceStatus>;
}

const notConnected = async (): Promise<SourceStatus> => ({
  enabled: false,
  reason: 'not_connected'
});

const healthConnectStatus = async (): Promise<SourceStatus> => {
  if (Capacitor.isNativePlatform()) {
    const res = await healthSyncService.checkPermissions();
    return res.granted
      ? { enabled: true, reason: 'granted' }
      : {
          enabled: false,
          reason: 'missing_permissions',
          detail:
            'No Health Connect data permissions granted. Open the source to review and authorize.'
        };
  }
  const synced = await db.user_source_status.get('health_connect');
  return synced?.connected
    ? { enabled: true, reason: 'granted' }
    : { enabled: false, reason: 'not_connected', detail: 'Available on Android' };
};

const seedStatus = async (): Promise<SourceStatus> => {
  const count = await db.measurement
    .where('source')
    .equals('seed')
    .filter((m) => !m.deleted_at)
    .count();
  return count > 0
    ? { enabled: true, reason: 'has_data' }
    : { enabled: false, reason: 'not_connected' };
};

const alwaysEnabled = async (): Promise<SourceStatus> => ({
  enabled: true,
  reason: 'always'
});

export const SOURCES: SourceEntry[] = [
  {
    id: 'health_connect',
    name: 'Android Health Connect',
    icon: 'smartphone',
    color: '#3ddc84',
    getStatus: healthConnectStatus
  },
  {
    id: 'apple_health',
    name: 'Apple Health',
    icon: 'favorite',
    color: '#ff2d55',
    getStatus: notConnected
  },
  {
    id: 'samsung_health',
    name: 'Samsung Health',
    icon: 'health-and-safety',
    color: '#1428a0',
    getStatus: notConnected
  },
  { id: 'oura', name: 'Oura Ring', icon: 'bedtime', color: '#1f2937', getStatus: notConnected },
  {
    id: 'garmin',
    name: 'Garmin Connect',
    icon: 'watch',
    color: '#007cc3',
    getStatus: notConnected
  },
  { id: 'manual', name: 'Manual Input', icon: 'edit', color: '#4f46e5', getStatus: alwaysEnabled },
  { id: 'seed', name: 'Dev Seed Data', icon: 'database', color: '#8b5cf6', getStatus: seedStatus }
];

export async function isSourceEnabled(sourceId: string): Promise<SourceStatus> {
  return SOURCES.find((s) => s.id === sourceId)?.getStatus() ?? notConnected();
}

/**
 * Report the device-local source connection state to the account so other
 * devices/web views reflect it. Only native platforms have device sources.
 */
export async function reportDeviceSourceStatus(): Promise<void> {
  if (!Capacitor.isNativePlatform()) return;
  const hc = await healthSyncService.checkPermissions();
  await updateSourceStatus('health_connect', hc.granted);
}
