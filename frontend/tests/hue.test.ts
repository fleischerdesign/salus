import { describe, it, expect } from 'vitest';
import { pointToHue, hueGradient } from '$lib/theme/hue';

describe('pointToHue', () => {
  const cx = 100;
  const cy = 100;

  it('maps top to 0°', () => {
    expect(pointToHue(100, 0, cx, cy)).toBe(0);
  });

  it('maps right to 90°', () => {
    expect(pointToHue(200, 100, cx, cy)).toBe(90);
  });

  it('maps bottom to 180°', () => {
    expect(pointToHue(100, 200, cx, cy)).toBe(180);
  });

  it('maps left to 270°', () => {
    expect(pointToHue(0, 100, cx, cy)).toBe(270);
  });

  it('always returns a value in 0..359', () => {
    expect(pointToHue(99, 0, cx, cy)).toBeGreaterThanOrEqual(0);
    expect(pointToHue(99, 0, cx, cy)).toBeLessThan(360);
  });
});

describe('hueGradient', () => {
  it('produces a conic gradient covering the full spectrum', () => {
    const gradient = hueGradient();

    expect(gradient.startsWith('conic-gradient(from 0deg,')).toBe(true);
    expect(gradient).toContain('oklch(0.7 0.15 0) 360deg');
  });
});
