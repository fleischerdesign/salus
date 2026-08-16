import type {
  HealthChangesResult,
  INativeHealthBridge,
  IngestedMetricPayload,
  PermissionStatusResult
} from '../types';

export class BrowserHealthBridge implements INativeHealthBridge {
  async isAvailable(): Promise<boolean> {
    return false;
  }

  async checkPermissions(): Promise<PermissionStatusResult> {
    return {
      granted: false,
      missingPermissions: ['requires_native_android_apk']
    };
  }

  async requestPermissions(): Promise<boolean> {
    return false;
  }

  async fetchDelta(_sinceIso: string): Promise<IngestedMetricPayload[]> {
    return [];
  }

  async getChangesToken(): Promise<string | null> {
    return null;
  }

  async getChanges(_token: string): Promise<HealthChangesResult> {
    return { metrics: [], nextToken: '' };
  }

  async openSettings(): Promise<boolean> {
    return false;
  }
}
