import { liveQuery } from 'dexie';

export function useQuery<T>(querier: () => Promise<T>): { value: T | undefined; loading: boolean } {
  let value = $state<T | undefined>(undefined);
  let loading = $state(true);

  $effect(() => {
    const sub = liveQuery(querier).subscribe({
      next: (v) => {
        value = v;
        loading = false;
      },
      error: () => {
        loading = false;
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
    }
  };
}
