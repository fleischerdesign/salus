import { Capacitor, registerPlugin } from '@capacitor/core';
import type {
  HealthChangesResult,
  HealthFetchResult,
  INativeHealthBridge,
  IngestedMetricPayload,
  PermissionStatusResult
} from '../types';

interface HealthConnectPluginNative {
  isAvailable(): Promise<{ available: boolean }>;
  checkPermissions(): Promise<{
    granted: boolean;
    grantedPermissions: string[];
    missing: string[];
  }>;
  requestPermissions(): Promise<{ granted: boolean }>;
  fetchDelta(options: {
    sinceIso: string;
    cursor?: string | null;
  }): Promise<{ metrics: IngestedMetricPayload[]; next_cursor: string }>;
  getChangesToken(): Promise<{ token: string }>;
  getChanges(options: {
    token: string;
  }): Promise<{ metrics: IngestedMetricPayload[]; token: string; expired: boolean }>;
  openHealthConnectSettings(): Promise<void>;
}

const HealthConnectPlugin = registerPlugin<HealthConnectPluginNative>('HealthConnectPlugin');

export class CapacitorHealthBridge implements INativeHealthBridge {
  async isAvailable(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      const res = await HealthConnectPlugin.isAvailable();
      return res.available;
    } catch {
      return false;
    }
  }

  async checkPermissions(): Promise<PermissionStatusResult> {
    if (!Capacitor.isNativePlatform()) {
      return { granted: false, missingPermissions: ['not_native'] };
    }
    try {
      const res = await HealthConnectPlugin.checkPermissions();
      return {
        granted: res.granted,
        grantedPermissions: res.grantedPermissions || [],
        missingPermissions: res.missing || []
      };
    } catch {
      return { granted: false, missingPermissions: ['plugin_error'] };
    }
  }

  async requestPermissions(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      const res = await HealthConnectPlugin.requestPermissions();
      return res.granted;
    } catch {
      return false;
    }
  }

  async fetchDelta(sinceIso: string, cursor?: string | null): Promise<HealthFetchResult> {
    if (!Capacitor.isNativePlatform()) return { metrics: [], nextCursor: '' };
    try {
      const res = await HealthConnectPlugin.fetchDelta({ sinceIso, cursor });
      return { metrics: res.metrics || [], nextCursor: res.next_cursor || '' };
    } catch {
      return { metrics: [], nextCursor: '' };
    }
  }

  async getChangesToken(): Promise<string | null> {
    if (!Capacitor.isNativePlatform()) return null;
    try {
      const res = await HealthConnectPlugin.getChangesToken();
      return res.token || null;
    } catch {
      return null;
    }
  }

  async getChanges(token: string): Promise<HealthChangesResult> {
    if (!Capacitor.isNativePlatform()) return { metrics: [], nextToken: '', expired: false };
    try {
      const res = await HealthConnectPlugin.getChanges({ token });
      return {
        metrics: res.metrics || [],
        nextToken: res.token || '',
        expired: res.expired || false
      };
    } catch {
      return { metrics: [], nextToken: '', expired: false };
    }
  }

  async openSettings(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      await HealthConnectPlugin.openHealthConnectSettings();
      return true;
    } catch {
      return false;
    }
  }
}
