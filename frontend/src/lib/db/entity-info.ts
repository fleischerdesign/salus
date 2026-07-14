import { getAuthHeaders } from '$lib/api/headers';

let _entityNames: Set<string> | null = null;
let _commandNames: Set<string> | null = null;

const HARDCODED_FALLBACK: Set<string> = new Set([
    'metric_type',
    'measurement',
    'goal',
    'circadian_profile',
    'exercise',
    'workout_plan',
    'workout_plan_exercise',
    'workout_session',
    'workout_log_entry',
    'insight',
    'notification',
    'dashboard_widget',
    'sharing_relationship',
    'leaderboard_group',
    'leaderboard_member',
    'share_recipient',
    'asymmetric_share',
    'user_profile',
    'admin_user',
    'admin_stats',
    'system_config',
    'api_token',
    'user',
    'community_activity',
    'federated_access_log'
]);

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
            return _entityNames;
        }
    } catch {
        /* fall back to hardcoded list */
    }

    _entityNames = HARDCODED_FALLBACK;
    return _entityNames;
}

export async function fetchCommands(): Promise<Set<string>> {
    if (_commandNames) return _commandNames;
    await fetchEntityNames();
    return _commandNames ?? new Set();
}

export function getEntityNames(): Set<string> {
    return _entityNames ?? HARDCODED_FALLBACK;
}

export function resetEntityNames(): void {
    _entityNames = null;
    _commandNames = null;
}
