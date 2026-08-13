const MOOD_NORMAL = [
  'bg-emerald-500',
  'bg-lime-400',
  'bg-amber-400',
  'bg-orange-400',
  'bg-red-400'
];

const MOOD_COLORBLIND = ['bg-blue-500', 'bg-sky-400', 'bg-gray-400', 'bg-orange-400', 'bg-red-500'];

/**
 * Maps a 1–10 mood score to a valence scale class. The colorblind variant
 * replaces the green→red scale with a blue→red scale, which stays
 * distinguishable for protan/deutan/tritan vision.
 */
export function moodColorClass(score: number, colorblind: boolean): string {
  const scale = colorblind ? MOOD_COLORBLIND : MOOD_NORMAL;
  if (score >= 8) return scale[0];
  if (score >= 6) return scale[1];
  if (score >= 4) return scale[2];
  if (score >= 2) return scale[3];
  return scale[4];
}
