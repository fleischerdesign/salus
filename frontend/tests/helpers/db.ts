import { db } from '$lib/db/database';

export async function resetDb(): Promise<void> {
  await db.delete();
  await db.open();
}

export async function seedMeta(key: string, value: unknown): Promise<void> {
  await db.meta.put({ key, value });
}
