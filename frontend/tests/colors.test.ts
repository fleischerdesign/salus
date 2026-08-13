import { describe, it, expect, beforeEach } from 'vitest';
import { theme } from '$stores/theme.svelte';
import { resolveColor, OKABE_ITO } from '$lib/theme/colors';

describe('resolveColor', () => {
  beforeEach(() => {
    localStorage.clear();
    theme.setColorblind(false);
  });

  it('returns the original color when colorblind mode is off', () => {
    expect(resolveColor('steps', '#f59e0b')).toBe('#f59e0b');
  });

  it('maps to an Okabe-Ito color when colorblind mode is on', () => {
    theme.setColorblind(true);

    const resolved = resolveColor('steps', '#f59e0b');

    expect(OKABE_ITO).toContain(resolved);
  });

  it('is deterministic per seed', () => {
    theme.setColorblind(true);

    expect(resolveColor('steps', '#f59e0b')).toBe(resolveColor('steps', '#f59e0b'));
  });

  it('never remaps achromatic colors', () => {
    theme.setColorblind(true);

    expect(resolveColor('white', '#ffffff')).toBe('#ffffff');
    expect(resolveColor('gray', '#9ca3af')).toBe('#9ca3af');
  });
});
