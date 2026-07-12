export interface PendingConflict {
  id: string;
  table: string;
  realId?: number;
  clientRecord: Record<string, unknown>;
  serverRecord: Record<string, unknown>;
  retryData?: Record<string, unknown>;
}

let _pending = $state<PendingConflict[]>([]);

export const conflictStore = {
  get current(): PendingConflict | null {
    return _pending[0] ?? null;
  },
  get hasPending(): boolean {
    return _pending.length > 0;
  },

  enqueue(conflict: PendingConflict): void {
    _pending = [..._pending, conflict];
  },

  resolve(id: string): void {
    _pending = _pending.filter((c) => c.id !== id);
  },
};
