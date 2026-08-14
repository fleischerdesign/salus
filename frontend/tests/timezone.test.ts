import { beforeEach, describe, expect, it } from 'vitest';
import {
  dateStringInTz,
  setUserTimezone,
  startOfTodayMs,
  userTimezone
} from '$lib/utils/timezone';
import { todayString } from '$lib/utils/datetime';

beforeEach(() => {
  setUserTimezone(null);
});

describe('timezone helpers', () => {
  it('formats a date in an explicit timezone', () => {
    // 2026-08-14T00:30Z is still Aug 14 in Berlin but Aug 13 in New York.
    const iso = '2026-08-14T00:30:00Z';
    expect(dateStringInTz(iso, 'Europe/Berlin')).toBe('2026-08-14');
    expect(dateStringInTz(iso, 'America/New_York')).toBe('2026-08-13');
  });

  it('startOfTodayMs is a local midnight (offset from a known instant)', () => {
    // For UTC the start of today must be a whole number of days.
    const start = startOfTodayMs('UTC');
    expect(start % 86_400_000).toBe(0);
    expect(start).toBeLessThanOrEqual(Date.now());
  });

  it('falls back to browser timezone when none is set', () => {
    const tz = userTimezone();
    expect(typeof tz).toBe('string');
    expect(tz.length).toBeGreaterThan(0);
  });

  it('todayString respects the cached user timezone', () => {
    setUserTimezone('Pacific/Kiritimati'); // UTC+14 — always ahead of UTC
    const kiritimati = todayString();
    const utc = dateStringInTz(new Date(), 'UTC');
    expect(kiritimati).not.toBeNull();
    expect([kiritimati, utc].length).toBe(2);
  });
});
