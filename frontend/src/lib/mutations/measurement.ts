import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const createMeasurement = (metricCode: string, data: Record<string, unknown>) => {
  const id = uuid7();
  const record = {
    id,
    user_id: 'self',
    metric_code: metricCode,
    ...data,
    created_at: now(),
    updated_at: null,
    deleted_at: null
  };
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'measurement',
    id,
    data: record,
    optimistic: record
  });
};

export const updateMeasurement = (measurementId: string, data: Record<string, unknown>) =>
  mutate({
    kind: 'crud',
    op: 'update',
    entity: 'measurement',
    id: measurementId,
    data,
    optimistic: { id: measurementId, ...data }
  });

export const deleteMeasurement = (measurementId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'measurement',
    id: measurementId,
    optimistic: { id: measurementId }
  });

export const createMetricType = (data: Record<string, unknown>) => {
  const id = uuid7();
  const record = {
    id,
    user_id: 'self',
    ...data,
    created_at: now(),
    updated_at: null,
    deleted_at: null
  };
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'user_metric_preference',
    id,
    data: record,
    optimistic: record
  });
};

export const updateMetricType = (metricTypeId: string, data: Record<string, unknown>) =>
  mutate({
    kind: 'crud',
    op: 'update',
    entity: 'user_metric_preference',
    id: metricTypeId,
    data,
    optimistic: { id: metricTypeId, ...data }
  });

export const deleteMetricType = (metricTypeId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'user_metric_preference',
    id: metricTypeId,
    optimistic: { id: metricTypeId }
  });
