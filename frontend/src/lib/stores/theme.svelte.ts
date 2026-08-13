export type ThemeMode = 'light' | 'dark' | 'system';

import { updateProfile } from '$lib/mutations/account';
import { localMode } from '$lib/db/local-mode.svelte';

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
    this.persist();
  }

  setColorblind(value: boolean): void {
    this.colorblind = value;
    this.persist();
  }

  setAccentHue(hue: number): void {
    this.accentHue = hue;
    this.persist();
  }

  previewAccentHue(hue: number): void {
    this.accentHue = hue;
    this.apply();
  }

  applyUserProfile(profile: {
    theme?: string;
    colorblind?: boolean;
    accent_hue?: number | null;
  }): void {
    if (profile.theme === 'light' || profile.theme === 'dark' || profile.theme === 'system') {
      this.mode = profile.theme;
    }
    if (typeof profile.colorblind === 'boolean') {
      this.colorblind = profile.colorblind;
    }
    if (
      typeof profile.accent_hue === 'number' &&
      Number.isInteger(profile.accent_hue) &&
      profile.accent_hue >= 0 &&
      profile.accent_hue < 360
    ) {
      this.accentHue = profile.accent_hue;
    }
    this.persistLocal();
    this.apply();
  }

  private persist(): void {
    this.persistLocal();
    this.apply();
    this.pushToServer();
  }

  private persistLocal(): void {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(THEME_KEY, this.mode);
    localStorage.setItem(COLORBLIND_KEY, String(this.colorblind));
    localStorage.setItem(ACCENT_KEY, String(this.accentHue));
  }

  private pushToServer(): void {
    if (localMode.active) return;
    updateProfile({
      theme: this.mode,
      colorblind: this.colorblind,
      accent_hue: this.accentHue
    });
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
