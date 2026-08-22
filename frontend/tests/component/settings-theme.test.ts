import { render, fireEvent } from '@testing-library/svelte';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import SettingsPage from '$components/pages/SettingsPage.svelte';
import { theme, ACCENT_HUES } from '$stores/theme.svelte';

// Appearance tab selection depends on the current route path.
vi.mock('$app/state', () => ({
  page: {
    url: {
      pathname: '/settings/app'
    }
  }
}));

vi.mock('$lib/mutations/account', () => ({
  updateProfile: vi.fn(() => Promise.resolve({ ok: true }))
}));

beforeEach(() => {
  localStorage.clear();
  theme.setMode('system');
  theme.setColorblind(false);
  theme.setAccentHue(290);
  theme.apply();
});

afterEach(() => {
  theme.apply();
});

function renderAppearance() {
  return render(SettingsPage, { initialTab: 'appearance' });
}

describe('SettingsPage appearance tab — theme wiring', () => {
  it('switches the theme mode via Hell / Dunkel / System buttons', async () => {
    const { getByText } = renderAppearance();

    await fireEvent.click(getByText('Dunkel'));
    expect(theme.mode).toBe('dark');
    expect(localStorage.getItem('salus_theme')).toBe('dark');

    theme.apply();
    expect(document.documentElement.dataset.theme).toBe('dark');

    await fireEvent.click(getByText('Hell'));
    expect(theme.mode).toBe('light');
    theme.apply();
    expect(document.documentElement.dataset.theme).toBe('light');

    await fireEvent.click(getByText('System'));
    expect(theme.mode).toBe('system');
  });

  it('highlights the active mode button', async () => {
    const { getByText } = renderAppearance();
    const dark = getByText('Dunkel');

    expect(dark.getAttribute('aria-pressed')).toBe('false');
    await fireEvent.click(dark);
    expect(dark.getAttribute('aria-pressed')).toBe('true');
  });

  it('toggles colorblind mode and applies data-colorblind to the document', async () => {
    const { getByRole } = renderAppearance();

    const toggle = getByRole('switch', { name: 'Farbenblind-Modus' });
    await fireEvent.click(toggle);

    expect(theme.colorblind).toBe(true);
    expect(localStorage.getItem('salus_colorblind')).toBe('true');
    theme.apply();
    expect(document.documentElement.dataset.colorblind).toBe('true');

    await fireEvent.click(toggle);
    expect(theme.colorblind).toBe(false);
    theme.apply();
    expect(document.documentElement.dataset.colorblind).toBeUndefined();
  });

  it('renders all eight accent preset chips with the active one highlighted', async () => {
    const { getByRole } = renderAppearance();

    for (const preset of ACCENT_HUES) {
      const chip = getByRole('button', { name: `Akzentfarbe: ${preset.name}` });
      expect(chip).not.toBeNull();
    }

    const grün = getByRole('button', { name: 'Akzentfarbe: Grün' });
    expect(grün.getAttribute('aria-pressed')).toBe('false');

    await fireEvent.click(grün);
    expect(theme.accentHue).toBe(160);
    expect(localStorage.getItem('salus_accent_hue')).toBe('160');
    expect(grün.getAttribute('aria-pressed')).toBe('true');
  });

  it('applies a preset hue to --accent-hue on the document root', async () => {
    const { getByRole } = renderAppearance();
    await fireEvent.click(getByRole('button', { name: 'Akzentfarbe: Rot' }));
    theme.apply();
    expect(document.documentElement.style.getPropertyValue('--accent-hue')).toBe('12');
  });

  it('adjusts the accent hue via HueRing keyboard interaction and persists the commit', async () => {
    const { getByRole } = renderAppearance();

    const ring = getByRole('slider', { name: 'Akzentfarbe' });
    expect(Number(ring.getAttribute('aria-valuenow'))).toBe(290);

    // ArrowRight previews + commits the next hue step.
    await fireEvent.keyDown(ring, { key: 'ArrowRight' });
    expect(theme.accentHue).toBe(291);
    expect(localStorage.getItem('salus_accent_hue')).toBe('291');

    // Shift+ArrowLeft steps by 10.
    await fireEvent.keyDown(ring, { key: 'ArrowLeft', shiftKey: true });
    expect(theme.accentHue).toBe(281);
    expect(localStorage.getItem('salus_accent_hue')).toBe('281');
  });
});
