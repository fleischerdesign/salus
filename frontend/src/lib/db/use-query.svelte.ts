import { liveQuery } from 'dexie';

/**
 * Reactive Dexie query subscription.
 *
 * Re-subscribes whenever the querier's reactive dependencies change (the
 * synchronous `querier()` call registers them with the active `$effect`),
 * so queries parameterized by component state stay live.
 */
export function useLive<T>(querier: () => Promise<T>, setValue: (v: T) => void): void {
  $effect(() => {
    querier();
    const sub = liveQuery(querier).subscribe({
      next: setValue,
      error: () => {}
    });
    return () => sub.unsubscribe();
  });
}

/**
 * Reactive query result for components that read `value`/`loading` instead
 * of targeting an existing state variable.
 */
export function useQuery<T>(querier: () => Promise<T>): { value: T | undefined; loading: boolean } {
  let value = $state<T | undefined>(undefined);
  let loading = $state(true);

  useLive(querier, (v) => {
    value = v;
    loading = false;
  });

  return {
    get value() {
      return value;
    },
    get loading() {
      return loading;
    }
  };
}
