import { db } from './database';

interface DatabaseDump {
  version: number;
  data: Record<string, unknown[]>;
}

/**
 * Serializes the entire Dexie store to a JSON string (full local backup).
 */
export async function exportDatabase(): Promise<string> {
  const data: Record<string, unknown[]> = {};
  for (const table of db.tables) {
    data[table.name] = await table.toArray();
  }
  return JSON.stringify({ version: 1, data });
}

/**
 * Restores the store from a previously exported JSON dump. Each table is
 * cleared and repopulated within a single write transaction.
 */
export async function importDatabase(json: string): Promise<void> {
  const parsed = JSON.parse(json) as DatabaseDump;
  if (!parsed || typeof parsed !== 'object' || !parsed.data || typeof parsed.data !== 'object') {
    throw new Error('Invalid backup file');
  }

  await db.transaction('rw', db.tables, async () => {
    for (const table of db.tables) {
      const rows = parsed.data[table.name];
      if (rows && Array.isArray(rows)) {
        await table.clear();
        await table.bulkPut(rows);
      }
    }
  });
}
