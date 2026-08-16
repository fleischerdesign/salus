import { Capacitor, registerPlugin } from '@capacitor/core';
import type {
  HealthChangesResult,
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
  fetchDelta(options: { sinceIso: string }): Promise<{ metrics: IngestedMetricPayload[] }>;
  getChangesToken(): Promise<{ token: string }>;
  getChanges(options: {
    token: string;
  }): Promise<{ metrics: IngestedMetricPayload[]; token: string }>;
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

  async fetchDelta(sinceIso: string): Promise<IngestedMetricPayload[]> {
    if (!Capacitor.isNativePlatform()) return [];
    try {
      const res = await HealthConnectPlugin.fetchDelta({ sinceIso });
      return res.metrics || [];
    } catch {
      return [];
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
    if (!Capacitor.isNativePlatform()) return { metrics: [], nextToken: '' };
    try {
      const res = await HealthConnectPlugin.getChanges({ token });
      return { metrics: res.metrics || [], nextToken: res.token || '' };
    } catch {
      return { metrics: [], nextToken: '' };
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
