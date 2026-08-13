import { network } from '$lib/native/network';

let online = $state(network.isOnline);

network.subscribe((value) => {
  online = value;
});

export function useOnline() {
  return {
    get isOnline() {
      return online;
    }
  };
}
