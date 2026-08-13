const KEY = 'salus_local_mode';

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
