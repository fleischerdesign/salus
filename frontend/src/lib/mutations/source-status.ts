import { mutate } from '$lib/mutate';
import { db } from '$lib/db/database';
import { nowIso } from '$lib/utils/datetime';
import type { UserSourceStatus } from '$lib/db/types';

/**
 * Report the account-level connection state of a data source. Idempotent:
 * the client id is the source id, so repeated reports upsert the same row.
 */
export const updateSourceStatus = async (source: string, connected: boolean) => {
  const id = source;
  const existing = await db.user_source_status.get(id);
  const record: UserSourceStatus = {
    id,
    user_id: existing?.user_id ?? '',
    source,
    connected,
    created_at: existing?.created_at ?? nowIso(),
    updated_at: nowIso()
  };

  await db.user_source_status.put(record);

  await mutate({
    kind: 'crud',
    op: 'update',
    entity: 'user_source_status',
    id,
    optimistic: { ...record }
  });
};
