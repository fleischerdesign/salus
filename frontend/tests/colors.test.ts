import { describe, it, expect, beforeEach } from 'vitest';
import { theme } from '$stores/theme.svelte';
import { resolveColor, OKABE_ITO } from '$lib/theme/colors';

describe('resolveColor', () => {
  beforeEach(() => {
    localStorage.clear();
    theme.setColorblind(false);
  });

  it('returns the original color when colorblind mode is off', () => {
    expect(resolveColor('#f59e0b')).toBe('#f59e0b');
  });

  it('maps to an Okabe-Ito color when colorblind mode is on', () => {
    theme.setColorblind(true);

    const resolved = resolveColor('#f59e0b');

    expect(OKABE_ITO).toContain(resolved);
  });

  it('preserves hue intent (warm maps to orange)', () => {
    theme.setColorblind(true);

    expect(resolveColor('#f59e0b')).toBe('#E69F00');
    expect(resolveColor('#10b981')).toBe('#009E73');
  });

  it('never remaps achromatic colors', () => {
    theme.setColorblind(true);

    expect(resolveColor('#ffffff')).toBe('#ffffff');
    expect(resolveColor('#9ca3af')).toBe('#9ca3af');
  });
});
