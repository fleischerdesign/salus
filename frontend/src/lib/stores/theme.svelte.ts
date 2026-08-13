export type ThemeMode = 'light' | 'dark' | 'system';

const THEME_KEY = 'salus_theme';
const COLORBLIND_KEY = 'salus_colorblind';
const ACCENT_KEY = 'salus_accent_hue';
const DEFAULT_ACCENT_HUE = 290;

export const ACCENT_HUES: ReadonlyArray<{ hue: number; label: string; color: string }> = [
  { hue: 290, label: 'Indigo', color: '#6366f1' },
  { hue: 250, label: 'Blau', color: '#3b82f6' },
  { hue: 190, label: 'Türkis', color: '#06b6d4' },
  { hue: 160, label: 'Grün', color: '#10b981' },
  { hue: 75, label: 'Amber', color: '#f59e0b' },
  { hue: 45, label: 'Orange', color: '#f97316' },
  { hue: 12, label: 'Rot', color: '#ef4444' },
  { hue: 340, label: 'Pink', color: '#ec4899' }
];

function readMode(): ThemeMode {
  if (typeof localStorage === 'undefined') return 'system';
  const value = localStorage.getItem(THEME_KEY);
  return value === 'light' || value === 'dark' ? value : 'system';
}

function readColorblind(): boolean {
  return typeof localStorage !== 'undefined' && localStorage.getItem(COLORBLIND_KEY) === 'true';
}

function readAccentHue(): number {
  if (typeof localStorage === 'undefined') return DEFAULT_ACCENT_HUE;
  const raw = localStorage.getItem(ACCENT_KEY);
  if (raw === null) return DEFAULT_ACCENT_HUE;
  const value = Number(raw);
  return Number.isInteger(value) && value >= 0 && value < 360 ? value : DEFAULT_ACCENT_HUE;
}

function prefersDark(): boolean {
  return (
    typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
  );
}

class ThemeService {
  mode = $state<ThemeMode>(readMode());
  colorblind = $state<boolean>(readColorblind());
  accentHue = $state<number>(readAccentHue());

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

  setAccentHue(hue: number): void {
    this.accentHue = hue;
    if (typeof localStorage !== 'undefined') localStorage.setItem(ACCENT_KEY, String(hue));
    this.apply();
  }

  apply(): void {
    if (typeof document === 'undefined') return;
    document.documentElement.dataset.theme = this.resolved;
    document.documentElement.style.setProperty('--accent-hue', String(this.accentHue));
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
