import { describe, expect, it } from 'vitest';
import { boundHint } from '$lib/utils/bounds';

const metric = { min_value: 0, max_value: 150_000, unit: 'steps' };

describe('boundHint', () => {
  it('returns null for empty input', () => {
    expect(boundHint('', metric)).toBeNull();
    expect(boundHint('   ', metric)).toBeNull();
  });

  it('returns null for non-numeric input', () => {
    expect(boundHint('abc', metric)).toBeNull();
  });

  it('returns null when in range', () => {
    expect(boundHint('8000', metric)).toBeNull();
    expect(boundHint('0', metric)).toBeNull();
    expect(boundHint('150000', metric)).toBeNull();
  });

  it('returns a hint below the minimum', () => {
    const hint = boundHint('-5', metric);
    expect(hint).toContain('plausible range');
    expect(hint).toContain('0–150000 steps');
  });

  it('returns a hint above the maximum', () => {
    const hint = boundHint('999999', metric);
    expect(hint).toContain('plausible range');
  });

  it('returns null when no bounds are defined', () => {
    expect(boundHint('12345', { min_value: null, max_value: null, unit: '' })).toBeNull();
  });

  it('handles a metric with only a maximum bound', () => {
    const hint = boundHint('300', { min_value: null, max_value: 200, unit: 'bpm' });
    expect(hint).toContain('−∞–200 bpm');
  });
});
