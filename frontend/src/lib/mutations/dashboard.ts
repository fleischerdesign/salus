import { mutate } from '$lib/mutate';
import { uuid7 } from '$lib/db/uuid';

export const addWidget = (metricTypeId: string, size = 'medium', position = 0) => {
  const id = uuid7();
  return mutate({
    kind: 'crud',
    op: 'create',
    entity: 'dashboard_widget',
    id,
    data: { id, metric_type_id: metricTypeId, size, position, config_json: '', is_visible: true },
    optimistic: {
      id,
      user_id: 'self',
      metric_type_id: metricTypeId,
      size,
      position,
      config_json: '',
      is_visible: true,
      created_at: new Date().toISOString(),
      updated_at: null,
      deleted_at: null
    }
  });
};

export const updateWidget = (widgetId: string, data: Record<string, unknown>) =>
  mutate({
    kind: 'crud',
    op: 'update',
    entity: 'dashboard_widget',
    id: widgetId,
    data,
    optimistic: { id: widgetId, ...data }
  });

export const deleteWidget = (widgetId: string) =>
  mutate({
    kind: 'crud',
    op: 'delete',
    entity: 'dashboard_widget',
    id: widgetId,
    optimistic: { id: widgetId }
  });
