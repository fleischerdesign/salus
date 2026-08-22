import { describe, expect, it } from 'vitest';
import { getCircadianArcState, type SolarTimes } from '$lib/analytics/views/circadian';

/**
 * Fixed synthetic solar times (Berlin-ish shape) so arc tests are deterministic
 * regardless of wall-clock/geography:
 *   sunrise 06:00 (360m) · solar noon 13:00 (780m) · sunset 20:00 (1200m) · nadir 01:00 (60m)
 */
const SOLAR: SolarTimes = {
  sunrise: '06:00',
  sunset: '20:00',
  solar_noon: '13:00',
  dawn: '05:30',
  dusk: '20:30',
  nadir: '01:00',
  sunrise_mins: 360,
  sunset_mins: 1200,
  solar_noon_mins: 780,
  dawn_mins: 330,
  dusk_mins: 1230,
  nadir_mins: 60
};

function at(hours: number, minutes: number) {
  return { hours, minutes };
}

describe('getCircadianArcState — day mode', () => {
  it('positions the sun at the base (progress 0) at sunrise', () => {
    const state = getCircadianArcState(at(6, 0), SOLAR);

    expect(state.mode).toBe('day');
    expect(state.celestialBody).toBe('sun');
    expect(state.progress).toBeCloseTo(0, 5);
    expect(state.celestialX).toBeCloseTo(5, 5);
    expect(state.celestialY).toBeCloseTo(75, 5);
    expect(state.startLabel).toBe('Sonnenaufgang');
    expect(state.startTime).toBe('06:00');
    expect(state.endLabel).toBe('Sonnenuntergang');
    expect(state.endTime).toBe('20:00');
    expect(state.currentPhase?.key).toBe('morning_light');
    expect(state.remainingTimeText).toBe('Noch 14 Std. 0 Min. Tageslicht');
  });

  it('peaks at the apex (progress ~0.5) at solar noon', () => {
    const state = getCircadianArcState(at(13, 0), SOLAR);

    expect(state.mode).toBe('day');
    expect(state.progress).toBeCloseTo(0.5, 5);
    expect(state.celestialX).toBeCloseTo(50, 5);
    expect(state.celestialY).toBeCloseTo(15, 5);
  });

  it('reaches the base (progress 1) at sunset', () => {
    const state = getCircadianArcState(at(20, 0), SOLAR);

    expect(state.mode).toBe('day');
    expect(state.progress).toBeCloseTo(1, 5);
    expect(state.celestialX).toBeCloseTo(95, 5);
    expect(state.celestialY).toBeCloseTo(75, 5);
    expect(state.currentPhase?.key).toBe('dusk_winddown');
    expect(state.remainingTimeText).toBe('Sonnenuntergang erreicht');
  });

  it('exposes all five physiological day phases on the day arc', () => {
    const state = getCircadianArcState(at(12, 0), SOLAR);

    expect(state.phases).toHaveLength(5);
    expect(state.phases.map((p) => p.key)).toEqual([
      'morning_light',
      'caffeine_window',
      'peak_focus',
      'afternoon_recovery',
      'dusk_winddown'
    ]);
    expect(state.phases.every((p) => p.progressStart >= 0 && p.progressEnd <= 1)).toBe(true);
    expect(state.phases.every((p) => p.startMins !== p.endMins)).toBe(true);
  });
});

describe('getCircadianArcState — night mode', () => {
  it('starts the moon at the base (progress ~0) just after sunset', () => {
    const state = getCircadianArcState(at(20, 1), SOLAR);

    expect(state.mode).toBe('night');
    expect(state.celestialBody).toBe('moon');
    expect(state.progress).toBeCloseTo(1 / 600, 5);
    expect(state.celestialX).toBeCloseTo(5 + (1 / 600) * 90, 5);
    expect(state.celestialY).toBeCloseTo(75 - 60 * Math.sin((1 / 600) * Math.PI), 5);
    expect(state.startLabel).toBe('Sonnenuntergang');
    expect(state.startTime).toBe('20:00');
    expect(state.endLabel).toBe('Sonnenaufgang');
    expect(state.endTime).toBe('06:00');
    expect(state.currentPhase?.key).toBe('blue_blocker');
    expect(state.remainingTimeText).toBe('Noch 9 Std. 59 Min. bis Sonnenaufgang');
  });

  it('peaks at the apex (progress ~0.5) at the night nadir', () => {
    const state = getCircadianArcState(at(1, 0), SOLAR);

    expect(state.mode).toBe('night');
    expect(state.progress).toBeCloseTo(0.5, 5);
    expect(state.celestialX).toBeCloseTo(50, 5);
    expect(state.celestialY).toBeCloseTo(15, 5);
    expect(state.currentPhase?.key).toBe('nadir_deep_sleep');
    expect(state.remainingTimeText).toBe('Noch 5 Std. 0 Min. bis Sonnenaufgang');
  });

  it('wraps across midnight and keeps advancing after 00:00', () => {
    const beforeMidnight = getCircadianArcState(at(23, 30), SOLAR); // 1410
    const afterMidnight = getCircadianArcState(at(1, 30), SOLAR); // 90

    expect(beforeMidnight.mode).toBe('night');
    expect(afterMidnight.mode).toBe('night');
    expect(beforeMidnight.progress).toBeCloseTo(210 / 600, 5);
    expect(afterMidnight.progress).toBeCloseTo(330 / 600, 5);
    expect(afterMidnight.progress).toBeGreaterThan(beforeMidnight.progress);

    // Both nights fall within the same 20:00 → 06:00 window.
    expect(afterMidnight.startTime).toBe('20:00');
    expect(beforeMidnight.startTime).toBe('20:00');
  });

  it('returns the moon to the base (progress 1) just before sunrise', () => {
    const state = getCircadianArcState(at(5, 59), SOLAR); // 359

    expect(state.mode).toBe('night');
    expect(state.progress).toBeCloseTo(599 / 600, 5);
    expect(state.celestialX).toBeCloseTo(5 + (599 / 600) * 90, 5);
    expect(state.celestialY).toBeCloseTo(75 - 60 * Math.sin((599 / 600) * Math.PI), 5);
    expect(state.currentPhase?.key).toBe('wake_prep');
  });

  it('exposes all five physiological night phases on the night arc', () => {
    const state = getCircadianArcState(at(0, 0), SOLAR);

    expect(state.phases).toHaveLength(5);
    expect(state.phases.map((p) => p.key)).toEqual([
      'blue_blocker',
      'melatonin_rise',
      'sleep_window',
      'nadir_deep_sleep',
      'wake_prep'
    ]);
    expect(state.phases.every((p) => p.progressStart >= 0 && p.progressEnd <= 1)).toBe(true);
  });
});
