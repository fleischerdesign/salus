import { describe, expect, it } from 'vitest';
import { aggregateDailyDeltas, measurementDailyDelta } from './daily-stats-core';

describe('measurementDailyDelta', () => {
  it('adds a create to the bucket', () => {
    const deltas = measurementDailyDelta('UTC', {
      metric_code: 'steps',
      start_time: '2026-08-16T10:00:00Z',
      value_numeric: 1000,
      deleted_at: null
    });
    expect(deltas).toEqual([{ metric_code: 'steps', day: '2026-08-16', count: 1, sum: 1000 }]);
  });

  it('removes the before-state and adds the after-state on a value change', () => {
    const deltas = measurementDailyDelta(
      'UTC',
      {
        metric_code: 'weight',
        start_time: '2026-08-16T10:00:00Z',
        value_numeric: 80,
        deleted_at: null
      },
      { start_time: '2026-08-16T10:00:00Z', value_numeric: 81 }
    );
    expect(deltas).toEqual([
      { metric_code: 'weight', day: '2026-08-16', count: -1, sum: -81 },
      { metric_code: 'weight', day: '2026-08-16', count: 1, sum: 80 }
    ]);
  });

  it('moves the bucket when the day changes', () => {
    const deltas = measurementDailyDelta(
      'UTC',
      {
        metric_code: 'weight',
        start_time: '2026-08-17T10:00:00Z',
        value_numeric: 80,
        deleted_at: null
      },
      { start_time: '2026-08-16T10:00:00Z', value_numeric: 81 }
    );
    expect(deltas).toEqual([
      { metric_code: 'weight', day: '2026-08-16', count: -1, sum: -81 },
      { metric_code: 'weight', day: '2026-08-17', count: 1, sum: 80 }
    ]);
  });

  it('only removes on a soft delete', () => {
    const deltas = measurementDailyDelta(
      'UTC',
      {
        metric_code: 'steps',
        start_time: '2026-08-16T10:00:00Z',
        value_numeric: 1000,
        deleted_at: '2026-08-17T00:00:00Z'
      },
      { start_time: '2026-08-16T10:00:00Z', value_numeric: 1000 }
    );
    expect(deltas).toEqual([{ metric_code: 'steps', day: '2026-08-16', count: -1, sum: -1000 }]);
  });

  it('ignores non-numeric measurements', () => {
    const deltas = measurementDailyDelta('UTC', {
      metric_code: 'sleep',
      start_time: '2026-08-16T10:00:00Z',
      value_numeric: null,
      deleted_at: null
    });
    expect(deltas).toEqual([]);
  });

  it('uses the given timezone for the local day', () => {
    // 2026-08-16T23:30Z is the 17th in UTC+2.
    const deltas = measurementDailyDelta('Europe/Berlin', {
      metric_code: 'steps',
      start_time: '2026-08-16T23:30:00Z',
      value_numeric: 100,
      deleted_at: null
    });
    expect(deltas[0].day).toBe('2026-08-17');
  });
});

describe('aggregateDailyDeltas', () => {
  it('merges per-measurement deltas into per-day buckets', () => {
    const buckets = aggregateDailyDeltas([
      { metric_code: 'steps', day: '2026-08-16', count: 1, sum: 100 },
      { metric_code: 'steps', day: '2026-08-16', count: 1, sum: 200 },
      { metric_code: 'steps', day: '2026-08-17', count: 1, sum: 150 }
    ]);
    expect(buckets.get('steps:2026-08-16')).toEqual({
      metric_code: 'steps',
      day: '2026-08-16',
      count: 2,
      sum: 300
    });
    expect(buckets.get('steps:2026-08-17')).toEqual({
      metric_code: 'steps',
      day: '2026-08-17',
      count: 1,
      sum: 150
    });
  });
});
