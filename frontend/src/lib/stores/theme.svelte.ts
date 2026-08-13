export type ThemeMode = 'light' | 'dark' | 'system';

const THEME_KEY = 'salus_theme';
const COLORBLIND_KEY = 'salus_colorblind';

function readMode(): ThemeMode {
  if (typeof localStorage === 'undefined') return 'system';
  const value = localStorage.getItem(THEME_KEY);
  return value === 'light' || value === 'dark' ? value : 'system';
}

function readColorblind(): boolean {
  return typeof localStorage !== 'undefined' && localStorage.getItem(COLORBLIND_KEY) === 'true';
}

function prefersDark(): boolean {
  return (
    typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
  );
}

class ThemeService {
  mode = $state<ThemeMode>(readMode());
  colorblind = $state<boolean>(readColorblind());

  get resolved(): 'light' | 'dark' {
    return this.mode === 'system' ? (prefersDark() ? 'dark' : 'light') : this.mode;
  }

  setMode(mode: ThemeMode): void {
    this.mode = mode;
    if (typeof localStorage !== 'undefined') localStorage.setItem(THEME_KEY, mode);
    this.apply();
  }

  setColorblind(value: boolean): void {
    this.colorblind = value;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(COLORBLIND_KEY, String(value));
    }
    this.apply();
  }

  apply(): void {
    if (typeof document === 'undefined') return;
    document.documentElement.dataset.theme = this.resolved;
    if (this.colorblind) {
      document.documentElement.dataset.colorblind = 'true';
    } else {
      delete document.documentElement.dataset.colorblind;
    }
  }

  init(): void {
    this.apply();
    if (typeof window !== 'undefined' && window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.mode === 'system') this.apply();
      });
    }
  }
}

export const theme = new ThemeService();
