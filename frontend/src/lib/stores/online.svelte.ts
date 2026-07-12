export function useOnline() {
  let online = $state(navigator.onLine);

  window.addEventListener('online', () => (online = true));
  window.addEventListener('offline', () => (online = false));

  return {
    get isOnline() {
      return online;
    },
  };
}
