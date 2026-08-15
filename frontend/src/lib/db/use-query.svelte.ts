import { liveQuery } from 'dexie';

export function useQuery<T>(
  querier: () => Promise<T>,
  deps?: () => unknown
): {
  value: T | undefined;
  loading: boolean;
  error: unknown;
} {
  let value = $state<T | undefined>(undefined);
  let loading = $state(true);
  let error = $state<unknown>(undefined);

  $effect(() => {
    // Track external reactive deps (dates, params, view modes). Dexie's liveQuery
    // runs the querier asynchronously, so reads inside it are invisible to Svelte;
    // invoking deps synchronously here re-subscribes when those inputs change.
    void deps?.();
    loading = true;

    const sub = liveQuery(querier).subscribe({
      next: (v) => {
        value = v;
        loading = false;
        error = undefined;
      },
      error: (e) => {
        loading = false;
        error = e;
      }
    });
    return () => sub.unsubscribe();
  });

  return {
    get value() {
      return value;
    },
    get loading() {
      return loading;
    },
    get error() {
      return error;
    }
  };
}
