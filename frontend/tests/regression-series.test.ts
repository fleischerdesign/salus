import { describe, expect, it } from 'vitest';
import { extractSleepDurations, regressionSeries } from '$lib/analytics/stats';

describe('regressionSeries', () => {
  it('returns null for fewer than 3 values', () => {
    expect(regressionSeries([1, 2])).toBeNull();
  });

  it('yields a flat regression for constant values', () => {
    const series = regressionSeries([5, 5, 5]);
    expect(series).not.toBeNull();
    expect(series!.slope).toBeCloseTo(0, 10);
  });

  it('computes slope, points, ci and n for a linear fit', () => {
    const series = regressionSeries([1, 2, 3]);
    expect(series).not.toBeNull();
    expect(series!.points).toHaveLength(3);
    expect(series!.ci).toHaveLength(3);
    expect(series!.n).toBe(3);
    expect(series!.slope).toBeCloseTo(1, 10);
  });
});

describe('extractSleepDurations', () => {
  it('uses value_numeric when present', () => {
    expect(extractSleepDurations([{ value_numeric: 7.5, value_json: null }])).toEqual([7.5]);
  });

  it('derives hours from value_json duration_seconds', () => {
    expect(
      extractSleepDurations([
        { value_numeric: null, value_json: JSON.stringify({ duration_seconds: 28800 }) }
      ])
    ).toEqual([8]);
  });

  it('ignores malformed value_json', () => {
    expect(extractSleepDurations([{ value_numeric: null, value_json: 'nope' }])).toEqual([]);
  });
});
