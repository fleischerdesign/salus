import { render } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import DataQualityPage from '../../src/routes/settings/data-quality/+page.svelte';

// The legacy /settings/data-quality URL must land on the Daten tab.
const state = vi.hoisted(() => ({ pathname: '/settings/data-quality' }));

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

describe('Data-quality settings route (backwards-compatible wrapper)', () => {
  it('renders the Daten settings tab for the legacy data-quality URL', () => {
    const { container } = render(DataQualityPage);

    const dataTab = [...container.querySelectorAll('a[href="/settings/data"]')][0];
    expect(dataTab).toBeDefined();
    expect(dataTab.textContent).toContain('Daten');
    expect(dataTab.getAttribute('aria-current')).toBe('page');

    expect(container.textContent).toContain('JSON-Komplettarchiv exportieren');
    expect(container.textContent).toContain('Lokaler Speicher (IndexedDB)');
  });
});
