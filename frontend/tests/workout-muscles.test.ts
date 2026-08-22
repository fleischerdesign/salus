import { describe, expect, it } from 'vitest';
import { formatMuscleName, parseMuscles } from '$lib/types/workouts';

describe('formatMuscleName', () => {
  it('converts single snake_case muscle tokens to Title Case', () => {
    expect(formatMuscleName('erector_spinae')).toBe('Erector Spinae');
    expect(formatMuscleName('gluteus_maximus')).toBe('Gluteus Maximus');
    expect(formatMuscleName('latissimus_dorsi')).toBe('Latissimus Dorsi');
    expect(formatMuscleName('deltoid_anterior')).toBe('Deltoid Anterior');
    expect(formatMuscleName('trapezius_mid_lower')).toBe('Trapezius Mid Lower');
    expect(formatMuscleName('rectus_abdominis')).toBe('Rectus Abdominis');
  });

  it('converts single lowercase words to Title Case', () => {
    expect(formatMuscleName('hamstrings')).toBe('Hamstrings');
    expect(formatMuscleName('forearms')).toBe('Forearms');
    expect(formatMuscleName('quadriceps')).toBe('Quadriceps');
    expect(formatMuscleName('rhomboids')).toBe('Rhomboids');
  });

  it('preserves existing Title Case, German, and multi-word names', () => {
    expect(formatMuscleName('Brust')).toBe('Brust');
    expect(formatMuscleName('Rücken')).toBe('Rücken');
    expect(formatMuscleName('Großer Gesäßmuskel')).toBe('Großer Gesäßmuskel');
    expect(formatMuscleName('Oberer Trapez / Nacken')).toBe('Oberer Trapez / Nacken');
  });

  it('handles null, undefined, empty, and whitespace strings safely', () => {
    expect(formatMuscleName(null)).toBe('');
    expect(formatMuscleName(undefined)).toBe('');
    expect(formatMuscleName('')).toBe('');
    expect(formatMuscleName('   ')).toBe('');
  });
});

describe('parseMuscles', () => {
  it('splits comma-separated muscle strings into trimmed tokens', () => {
    expect(parseMuscles('erector_spinae, gluteus_maximus, hamstrings')).toEqual([
      'erector_spinae',
      'gluteus_maximus',
      'hamstrings'
    ]);
  });

  it('trims extra whitespace around tokens', () => {
    expect(parseMuscles('  latissimus_dorsi  ,   rhomboids   ')).toEqual([
      'latissimus_dorsi',
      'rhomboids'
    ]);
  });

  it('handles single muscle token', () => {
    expect(parseMuscles('biceps_brachii')).toEqual(['biceps_brachii']);
  });

  it('handles null, undefined, and empty string safely', () => {
    expect(parseMuscles(null)).toEqual([]);
    expect(parseMuscles(undefined)).toEqual([]);
    expect(parseMuscles('')).toEqual([]);
    expect(parseMuscles('   ')).toEqual([]);
  });
});

describe('plan focus deduplication integration', () => {
  it('parses, formats, and deduplicates muscles across multiple exercises', () => {
    const exercises = [
      { primary_muscles: 'erector_spinae, gluteus_maximus, hamstrings' },
      { primary_muscles: 'latissimus_dorsi, trapezius_mid_lower' },
      { primary_muscles: 'gluteus_maximus, hamstrings' },
      { primary_muscles: null },
      { primary_muscles: '' },
      { primary_muscles: 'latissimus_dorsi' }
    ];

    const focusSet = new Set<string>();
    for (const ex of exercises) {
      for (const token of parseMuscles(ex.primary_muscles)) {
        const formatted = formatMuscleName(token);
        if (formatted) {
          focusSet.add(formatted);
        }
      }
    }

    const uniqueMuscles = Array.from(focusSet);
    expect(uniqueMuscles).toEqual([
      'Erector Spinae',
      'Gluteus Maximus',
      'Hamstrings',
      'Latissimus Dorsi',
      'Trapezius Mid Lower'
    ]);

    // Ensure no single tag contains commas
    for (const tag of uniqueMuscles) {
      expect(tag).not.toContain(',');
    }

    // Top 3 badges
    const topBadges = uniqueMuscles.slice(0, 3);
    expect(topBadges).toHaveLength(3);
    expect(topBadges).toEqual(['Erector Spinae', 'Gluteus Maximus', 'Hamstrings']);
  });
});
