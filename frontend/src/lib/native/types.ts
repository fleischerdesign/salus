export interface IngestedMetricPayload {
  metric_code: string;
  value: number;
  measured_at: string;
  source: 'health_connect' | 'samsung_health' | 'manual';
  source_data_type?: string;
  external_id: string;
}

export interface PermissionStatusResult {
  granted: boolean;
  missingPermissions: string[];
}

export interface INativeHealthBridge {
  isAvailable(): Promise<boolean>;
  checkPermissions(): Promise<PermissionStatusResult>;
  requestPermissions(): Promise<boolean>;
  fetchDelta(sinceIso: string): Promise<IngestedMetricPayload[]>;
}

export interface LocalNotificationPayload {
  id: number;
  title: string;
  body: string;
  scheduleAt?: Date;
  actionButtons?: Array<{ id: string; title: string }>;
  extraData?: Record<string, unknown>;
}

export interface INotificationProvider {
  requestPermissions(): Promise<boolean>;
  schedule(payload: LocalNotificationPayload): Promise<void>;
  cancel(id: number): Promise<void>;
}

export interface NativeDeviceInfo {
  model: string;
  platform: 'android' | 'web';
  operatingSystem: string;
  osVersion: string;
  manufacturer: string;
  batteryLevel?: number;
  isCharging?: boolean;
}

export interface IDeviceInfoService {
  getDeviceInfo(): Promise<NativeDeviceInfo>;
}
