import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

function now(): string {
  return new Date().toISOString();
}

export const createMeasurement = (metricTypeId: string, data: Record<string, unknown>) => {
  const id = uuid7();
  const record = {
    id,
    user_id: 'self',
    metric_type_id: metricTypeId,
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
    is_system: false,
    ...data,
    created_at: now(),
    updated_at: null,
    deleted_at: null
  };
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'metric_type',
    id,
    data: record,
    optimistic: record
  });
};

export const updateMetricType = (metricTypeId: string, data: Record<string, unknown>) =>
  mutate({
    kind: 'crud',
    op: 'update',
    entity: 'metric_type',
    id: metricTypeId,
    data,
    optimistic: { id: metricTypeId, ...data }
  });

export const deleteMetricType = (metricTypeId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'metric_type',
    id: metricTypeId,
    optimistic: { id: metricTypeId }
  });
