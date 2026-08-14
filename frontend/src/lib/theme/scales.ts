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

const MOOD_GRADIENTS_NORMAL = [
  'from-red-500 to-red-400',
  'from-red-400 to-orange-400',
  'from-orange-400 to-amber-400',
  'from-amber-400 to-yellow-400',
  'from-yellow-400 to-lime-400',
  'from-lime-400 to-emerald-400',
  'from-emerald-400 to-teal-400',
  'from-teal-400 to-cyan-400',
  'from-cyan-400 to-blue-400',
  'from-blue-400 to-indigo-400'
];

const MOOD_GRADIENTS_COLORBLIND = [
  'from-red-500 to-red-400',
  'from-red-400 to-orange-400',
  'from-orange-400 to-amber-400',
  'from-amber-400 to-yellow-400',
  'from-yellow-400 to-gray-400',
  'from-gray-400 to-blue-400',
  'from-blue-400 to-blue-500',
  'from-blue-500 to-sky-500',
  'from-sky-500 to-cyan-500',
  'from-cyan-500 to-indigo-500'
];

/**
 * Maps a 1–10 mood score to a two-stop gradient for the mood picker, matching
 * moodColorClass. The colorblind variant shifts the positive end green→blue.
 */
export function moodGradient(score: number, colorblind: boolean): string {
  const scale = colorblind ? MOOD_GRADIENTS_COLORBLIND : MOOD_GRADIENTS_NORMAL;
  const index = Math.max(0, Math.min(9, Math.round(score) - 1));
  return scale[index];
}
