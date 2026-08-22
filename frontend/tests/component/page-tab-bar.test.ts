import { render } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import CommunityPage from '$components/pages/CommunityPage.svelte';
import NutritionPage from '$components/pages/NutritionPage.svelte';
import WorkoutsPage from '$components/pages/WorkoutsPage.svelte';

// Mutable pathname so each page test can drive the tab bar's active state.
const state = vi.hoisted(() => ({ pathname: '/community/leaderboard' }));

vi.mock('$app/state', () => ({
  page: {
    url: {
      get pathname() {
        return state.pathname;
      }
    }
  }
}));

vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

// Icon colors must never be hardcoded per tab, nor must they duplicate the
// parent control's active/inactive text state.
const FORBIDDEN_ICON_CLASSES = [
  'text-circadian',
  'text-activity',
  'text-primary',
  'text-vital',
  'text-text-muted',
  'text-text-main'
];

type Tab = { label: string; active: boolean };

function tabBar(container: HTMLElement, label: string): HTMLElement {
  const control = [...container.querySelectorAll('a,button')].find((n) =>
    n.textContent?.includes(label)
  );
  expect(control, `tab control for "${label}" should exist`).toBeDefined();
  const bar = control!.closest('div');
  expect(bar, `tab bar containing "${label}" should exist`).toBeDefined();
  return bar as HTMLElement;
}

function assertTabBar(container: HTMLElement, tabs: Tab[]): void {
  const bar = tabBar(container, tabs[0].label);
  const controls = [...bar.querySelectorAll('a,button')];

  for (const tab of tabs) {
    const control = controls.find((n) => n.textContent?.includes(tab.label));
    expect(control, `tab "${tab.label}" should exist`).toBeDefined();
    expect(
      tab.active ? control!.className.includes('text-primary') : control!.className.includes('text-text-muted'),
      `tab "${tab.label}" should carry the ${tab.active ? 'active' : 'inactive'} color on the control`
    ).toBe(true);
  }

  // Every icon inside the tab bar inherits color from its parent control.
  const icons = [...bar.querySelectorAll('span[role="img"]')];
  expect(icons.length).toBeGreaterThan(0);
  for (const icon of icons) {
    for (const forbidden of FORBIDDEN_ICON_CLASSES) {
      expect(icon.className, `tab icon must not carry "${forbidden}"`).not.toContain(forbidden);
    }
  }
}

describe('page-level tab bars inherit icon color from the parent control', () => {
  it('CommunityPage tab icons inherit active/inactive color', () => {
    state.pathname = '/community/leaderboard';
    const { container } = render(CommunityPage);
    assertTabBar(container, [
      { label: 'Challenges & Ranglisten', active: true },
      { label: 'Freunde & Verbindungen', active: false },
      { label: 'Aktivitätsfeed', active: false }
    ]);
  });

  it('NutritionPage tab icons inherit active/inactive color', () => {
    const { container } = render(NutritionPage);
    assertTabBar(container, [
      { label: 'Tagebuch', active: true },
      { label: 'Rezeptdatenbank', active: false },
      { label: 'Lebensmittelkatalog', active: false }
    ]);
  });

  it('WorkoutsPage tab icons inherit active/inactive color', () => {
    state.pathname = '/workouts/plans';
    const { container } = render(WorkoutsPage);
    assertTabBar(container, [
      { label: 'Workouts', active: true },
      { label: 'Programme', active: false },
      { label: 'Historie', active: false },
      { label: 'Übungen', active: false }
    ]);
  });
});