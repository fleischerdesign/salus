import Dexie from 'dexie';
import { describe, expect, it } from 'vitest';
import { measurementPageBounds } from './measurement-paging';

describe('measurementPageBounds', () => {
  it('bounds the top page to the metric across all times', () => {
    const b = measurementPageBounds('heart_rate', { mode: 'top' });
    expect(b.lower).toEqual(['heart_rate', Dexie.minKey]);
    expect(b.upper).toEqual(['heart_rate', Dexie.maxKey]);
    expect(b.includeLower).toBe(true);
    expect(b.includeUpper).toBe(true);
  });

  it('bounds the older page strictly below the cursor time, still inside the metric', () => {
    const b = measurementPageBounds('heart_rate', { mode: 'older', time: '2026-08-16T14:25:00Z' });
    expect(b.lower).toEqual(['heart_rate', Dexie.minKey]);
    expect(b.upper).toEqual(['heart_rate', '2026-08-16T14:25:00Z']);
    expect(b.includeLower).toBe(true);
    expect(b.includeUpper).toBe(false);
  });

  it('bounds the newer page strictly above the cursor time, still inside the metric', () => {
    const b = measurementPageBounds('heart_rate', { mode: 'newer', time: '2026-08-16T14:25:00Z' });
    expect(b.lower).toEqual(['heart_rate', '2026-08-16T14:25:00Z']);
    expect(b.upper).toEqual(['heart_rate', Dexie.maxKey]);
    expect(b.includeLower).toBe(false);
    expect(b.includeUpper).toBe(true);
  });
});
