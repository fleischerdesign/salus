import { describe, it, expect } from 'vitest';
import { moodColorClass, moodGradient } from '$lib/theme/scales';

describe('moodColorClass', () => {
  it('maps high scores to green by default', () => {
    expect(moodColorClass(9, false)).toBe('bg-emerald-500');
  });

  it('maps high scores to blue in colorblind mode', () => {
    expect(moodColorClass(9, true)).toBe('bg-blue-500');
  });

  it('maps low scores to red in both modes', () => {
    expect(moodColorClass(1, false)).toBe('bg-red-400');
    expect(moodColorClass(1, true)).toBe('bg-red-500');
  });
});

describe('moodGradient', () => {
  it('returns a red gradient for the lowest score', () => {
    expect(moodGradient(1, false)).toBe('from-red-500 to-red-400');
  });

  it('returns a blue gradient for the highest score by default', () => {
    expect(moodGradient(10, false)).toBe('from-blue-400 to-indigo-400');
  });

  it('clamps out-of-range scores', () => {
    expect(moodGradient(0, false)).toBe('from-red-500 to-red-400');
    expect(moodGradient(11, true)).toBe('from-cyan-500 to-indigo-500');
  });
});
