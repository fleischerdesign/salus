const KEY = 'salus_local_mode';

export const SERVER_ONLY_PATH_PREFIXES = ['/community', '/admin', '/coach/chat'];

class LocalModeService {
  active = $state(typeof localStorage !== 'undefined' && localStorage.getItem(KEY) === 'true');

  enable(): void {
    this.active = true;
    if (typeof localStorage !== 'undefined') localStorage.setItem(KEY, 'true');
  }

  disable(): void {
    this.active = false;
    if (typeof localStorage !== 'undefined') localStorage.removeItem(KEY);
  }
}

export const localMode = new LocalModeService();
