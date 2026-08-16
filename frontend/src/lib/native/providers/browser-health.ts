import type {
  HealthChangesResult,
  HealthFetchResult,
  INativeHealthBridge,
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

  async fetchDelta(_sinceIso: string, _cursor?: string | null): Promise<HealthFetchResult> {
    return { metrics: [], nextCursor: '' };
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
