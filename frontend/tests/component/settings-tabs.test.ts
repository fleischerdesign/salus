import { render } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import { addCollection } from '@iconify/svelte/dist/offline-functions.js';
import SettingsPage from '$components/pages/SettingsPage.svelte';
import icons from '$lib/icons.json';

// The root layout normally registers the icon bundle; component tests bypass it.
addCollection(icons);

// Mutable pathname so each scenario can drive the active tab.
const state = vi.hoisted(() => ({ pathname: '/settings/account' }));

vi.mock('$app/state', () => ({
  page: {
    url: {
      get pathname() {
        return state.pathname;
      }
    }
  }
}));

vi.mock('$lib/mutations/account', () => ({
  updateProfile: vi.fn(() => Promise.resolve({ ok: true }))
}));

const EXPECTED_TABS = [
  { id: 'account', label: 'Profil', path: '/settings/account', icon: 'person' },
  { id: 'appearance', label: 'Erscheinungsbild', path: '/settings/app', icon: 'palette' },
  { id: 'security', label: 'Sicherheit', path: '/settings/security', icon: 'lock' },
  { id: 'sources', label: 'Quellen', path: '/settings/sources', icon: 'sensors' },
  {
    id: 'notifications',
    label: 'Benachrichtigungen',
    path: '/settings/notifications',
    icon: 'notifications'
  },
  { id: 'shares', label: 'Freigaben', path: '/settings/shares', icon: 'share' },
  { id: 'data', label: 'Daten', path: '/settings/data', icon: 'database' }
] as const;

// Icon colors must never be hardcoded per tab, nor duplicate the parent
// control's active/inactive text state.
const FORBIDDEN_ICON_CLASSES = [
  'text-circadian',
  'text-activity',
  'text-primary',
  'text-vital',
  'text-text-muted',
  'text-text-main'
];

function tabAnchors(container: HTMLElement): HTMLAnchorElement[] {
  return [...container.querySelectorAll<HTMLAnchorElement>('a[href^="/settings/"]')];
}

function iconPathD(iconName: string): string {
  const body = (icons.icons as Record<string, { body: string }>)[iconName]?.body;
  const match = body?.match(/d="([^"]+)"/);
  expect(match, `icon "${iconName}" must exist in the icon bundle`).toBeTruthy();
  return match![1];
}

describe('SettingsPage single-word navigation tabs', () => {
  it('renders exactly the seven tabs in order with the correct labels and paths', () => {
    state.pathname = '/settings/account';
    const { container } = render(SettingsPage, { initialTab: 'account' });

    const tabs = tabAnchors(container);
    expect(tabs).toHaveLength(7);

    tabs.forEach((tab, index) => {
      const expected = EXPECTED_TABS[index];
      expect(tab.getAttribute('href')).toBe(expected.path);
      expect(tab.textContent).toContain(expected.label);
    });
  });

  it('uses no ampersand or "und" concatenation in any tab label', () => {
    state.pathname = '/settings/account';
    const { container } = render(SettingsPage, { initialTab: 'account' });

    const tabs = tabAnchors(container);
    for (const [index, tab] of tabs.entries()) {
      const expected = EXPECTED_TABS[index];

      const labelSpan = [...tab.querySelectorAll('span')].find(
        (s) => s.getAttribute('role') !== 'img' && s.textContent === expected.label
      );
      expect(labelSpan, `label span for tab "${expected.label}" should exist`).toBeDefined();

      expect(expected.label).not.toContain('&');
      expect(expected.label).not.toContain('und');
      expect(expected.label.split(/\s+/)).toHaveLength(1);
    }
  });

  it('renders the correct icon inside every tab', () => {
    state.pathname = '/settings/account';
    const { container } = render(SettingsPage, { initialTab: 'account' });

    const tabs = tabAnchors(container);
    for (const [index, tab] of tabs.entries()) {
      const expected = EXPECTED_TABS[index];
      const svg = tab.querySelector('svg');
      expect(svg, `tab "${expected.label}" should render an icon`).not.toBeNull();

      const dValues = [...svg!.querySelectorAll('path')].map((p) => p.getAttribute('d'));
      expect(dValues, `tab "${expected.label}" should render its "${expected.icon}" icon`).toContain(
        iconPathD(expected.icon)
      );
    }
  });

  it('does not hardcode color classes on tab icons', () => {
    state.pathname = '/settings/account';
    const { container } = render(SettingsPage, { initialTab: 'account' });

    const icons = [...container.querySelectorAll('span[role="img"]')];
    expect(icons.length).toBeGreaterThanOrEqual(7);
    for (const icon of icons) {
      for (const forbidden of FORBIDDEN_ICON_CLASSES) {
        expect(icon.className, `tab icon must not carry "${forbidden}"`).not.toContain(forbidden);
      }
    }
  });

  it('highlights the tab matching the current route', () => {
    for (const expected of EXPECTED_TABS) {
      state.pathname = expected.path;
      const { container } = render(SettingsPage, { initialTab: expected.id });

      for (const tab of tabAnchors(container)) {
        const isExpected = tab.getAttribute('href') === expected.path;
        expect(tab.getAttribute('aria-current')).toBe(isExpected ? 'page' : null);
        if (isExpected) {
          expect(tab.className).toContain('text-primary');
          expect(tab.className).not.toContain('text-text-muted');
        } else {
          expect(tab.className).toContain('text-text-muted');
          expect(tab.className).not.toContain('text-primary');
        }
      }
    }
  });

  it('falls back to initialTab when the route does not map to a settings tab', () => {
    state.pathname = '/settings';
    const { container } = render(SettingsPage, { initialTab: 'security' });

    const security = tabAnchors(container).find((t) => t.getAttribute('href') === '/settings/security');
    expect(security?.getAttribute('aria-current')).toBe('page');
    expect(security?.className).toContain('text-primary');
  });
});
