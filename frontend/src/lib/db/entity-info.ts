import { getAuthHeaders } from '$lib/api/headers';
import { db } from './database';

let _entityNames: Set<string> | null = null;
let _commandNames: Set<string> | null = null;

const META_KEY_ENTITIES = 'sync:entity_names';
const META_KEY_COMMANDS = 'sync:command_names';

interface SyncManifest {
  entities: Array<{ name: string; strategy: string }>;
  commands: string[];
}

export async function fetchEntityNames(): Promise<Set<string>> {
  if (_entityNames) return _entityNames;

  try {
    const headers = { ...getAuthHeaders(), Accept: 'application/json' };
    const res = await fetch('/api/v1/sync/entities', { headers });
    if (res.ok) {
      const data = (await res.json()) as SyncManifest;
      _entityNames = new Set(data.entities.map((e) => e.name));
      _commandNames = new Set(data.commands);
      db.meta.put({ key: META_KEY_ENTITIES, value: [..._entityNames] });
      db.meta.put({ key: META_KEY_COMMANDS, value: [..._commandNames] });
      return _entityNames;
    }
  } catch {
    /* network unavailable — fall back to Dexie cache */
  }

  const cached = await db.meta.get(META_KEY_ENTITIES);
  _entityNames = cached?.value ? new Set(cached.value as string[]) : new Set();
  return _entityNames;
}

export async function fetchCommands(): Promise<Set<string>> {
  if (_commandNames) return _commandNames;
  await fetchEntityNames();
  if (_commandNames) return _commandNames;
  const cached = await db.meta.get(META_KEY_COMMANDS);
  _commandNames = cached?.value ? new Set(cached.value as string[]) : new Set();
  return _commandNames;
}

export function getEntityNames(): Set<string> {
  return _entityNames ?? new Set();
}

export function resetEntityNames(): void {
  _entityNames = null;
  _commandNames = null;
}
