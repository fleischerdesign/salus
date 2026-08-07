import { Capacitor, registerPlugin } from '@capacitor/core';
import type { INativeHealthBridge, IngestedMetricPayload, PermissionStatusResult } from '../types';

interface HealthConnectPluginNative {
  isAvailable(): Promise<{ available: boolean }>;
  checkPermissions(): Promise<{ granted: boolean; missing: string[] }>;
  requestPermissions(): Promise<{ granted: boolean }>;
  fetchDelta(options: { sinceIso: string }): Promise<{ metrics: IngestedMetricPayload[] }>;
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
      return { granted: res.granted, missingPermissions: res.missing || [] };
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
}
