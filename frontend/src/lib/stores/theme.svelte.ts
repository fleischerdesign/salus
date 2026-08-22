export type ThemeMode = 'light' | 'dark' | 'system';

import { MediaQuery } from 'svelte/reactivity';
import { updateProfile } from '$lib/mutations/account';
import { localMode } from '$lib/db/local-mode.svelte';

const THEME_KEY = 'salus_theme';
const COLORBLIND_KEY = 'salus_colorblind';
const ACCENT_KEY = 'salus_accent_hue';
const DEFAULT_ACCENT_HUE = 290;

export const ACCENT_HUES: ReadonlyArray<{ name: string; hue: number; color: string }> = [
  { name: 'Indigo', hue: 290, color: '#6366f1' },
  { name: 'Blau', hue: 250, color: '#3b82f6' },
  { name: 'Türkis', hue: 190, color: '#06b6d4' },
  { name: 'Grün', hue: 160, color: '#10b981' },
  { name: 'Amber', hue: 75, color: '#f59e0b' },
  { name: 'Orange', hue: 45, color: '#f97316' },
  { name: 'Rot', hue: 12, color: '#ef4444' },
  { name: 'Pink', hue: 340, color: '#ec4899' }
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

class ThemeService {
  mode = $state<ThemeMode>(readMode());
  colorblind = $state<boolean>(readColorblind());
  accentHue = $state<number>(readAccentHue());

  private _darkQuery: MediaQuery | null = null;

  private get darkQuery(): MediaQuery | null {
    if (this._darkQuery === null && typeof window !== 'undefined') {
      this._darkQuery = new MediaQuery('(prefers-color-scheme: dark)');
    }
    return this._darkQuery;
  }

  get resolved(): 'light' | 'dark' {
    return this.mode === 'system' ? (this.darkQuery?.current ? 'dark' : 'light') : this.mode;
  }

  setMode(mode: ThemeMode): void {
    this.mode = mode;
    this.persist();
  }

  toggle(): void {
    this.setMode(this.resolved === 'dark' ? 'light' : 'dark');
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
  }

  private persist(): void {
    this.persistLocal();
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
}

export const theme = new ThemeService();
