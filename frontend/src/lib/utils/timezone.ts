/**
 * User timezone — the single source for "local day" computation on the client.
 *
 * The IANA timezone comes from the synced user profile (`User.timezone`). It is
 * cached synchronously (populated at bootstrap, refreshed on profile change) so
 * `todayString()`/`dateString()` stay synchronous for all existing callers.
 * Before the profile loads, or for invalid zones, we fall back to the browser's
 * local timezone — which matches the single-device default.
 */

let cachedTz: string | null = null;

export function setUserTimezone(tz: string | null | undefined): void {
  cachedTz = tz && tz.trim() ? tz.trim() : null;
}

export function userTimezone(): string {
  if (cachedTz) return cachedTz;
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
}

/** Local `YYYY-MM-DD` for an instant (ISO string or Date) in a timezone. */
export function dateStringInTz(value: string | Date, tz: string): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: tz,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(new Date(value));
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? '';
  return `${get('year')}-${get('month')}-${get('day')}`;
}

function wallParts(tz: string, d: Date) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: tz,
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).formatToParts(d);
  const get = (type: string) => Number(parts.find((p) => p.type === type)?.value ?? 0);
  return {
    year: get('year'),
    month: get('month'),
    day: get('day'),
    hour: get('hour'),
    minute: get('minute'),
    second: get('second')
  };
}

/** Offset (ms) of a timezone at a given instant. */
export function offsetMsAt(tz: string, at: Date): number {
  const p = wallParts(tz, at);
  const asUTC = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute, p.second);
  return asUTC - Math.floor(at.getTime() / 1000) * 1000;
}

/** Offset in decimal hours (e.g. +2 for CEST) of a timezone at a given instant. */
export function getTimezoneOffsetHours(tz: string, at: Date = new Date()): number {
  return offsetMsAt(tz, at) / (1000 * 60 * 60);
}

/**
 * Epoch (ms) of local midnight for a `YYYY-MM-DD` calendar date in a timezone.
 *
 * The wall-clock→epoch conversion is a fixed point (the offset is piecewise
 * constant, changing only at DST transitions), so a couple of iterations resolve
 * the exact midnight even across spring-forward/fall-back days.
 */
export function startOfLocalDayMs(dateStr: string, tz: string): number {
  const asUTC = Date.parse(`${dateStr}T00:00:00Z`);
  let epoch = asUTC;
  for (let i = 0; i < 3; i++) {
    epoch = asUTC - offsetMsAt(tz, new Date(epoch));
  }
  return epoch;
}

/** Millisecond epoch of local midnight (start of today) in a timezone. */
export function startOfTodayMs(tz: string): number {
  return startOfLocalDayMs(dateStringInTz(new Date(), tz), tz);
}
