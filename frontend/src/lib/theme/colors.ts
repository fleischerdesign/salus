import { theme } from '$stores/theme.svelte';

// Okabe-Ito: a categorical palette distinguishable for protan/deutan/tritan vision.
export const OKABE_ITO: readonly string[] = [
  '#0072B2', // blue
  '#E69F00', // orange
  '#009E73', // green
  '#D55E00', // vermillion
  '#CC79A7', // reddish purple
  '#56B4E9', // sky blue
  '#F0E442', // yellow
  '#000000' // black
];

function hashString(input: string): number {
  let hash = 5381;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 33) ^ input.charCodeAt(i);
  }
  return hash >>> 0;
}

function isNeutral(hex: string): boolean {
  const match = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!match) return true;
  const r = parseInt(match[1].slice(0, 2), 16);
  const g = parseInt(match[1].slice(2, 4), 16);
  const b = parseInt(match[1].slice(4, 6), 16);
  return Math.abs(r - g) < 40 && Math.abs(g - b) < 40 && Math.abs(r - b) < 40;
}

/**
 * Resolves a categorical color for the active accessibility mode. When the
 * colorblind mode is off, returns the original color unchanged. When on,
 * returns a deterministic Okabe-Ito color derived from the stable `seed`, so
 * the same entity always maps to the same colorblind-safe color. Achromatic
 * colors (white/black/gray) are neutral, never categorical, and pass through.
 */
export function resolveColor(seed: string, original: string): string {
  if (!theme.colorblind || isNeutral(original)) return original;
  return OKABE_ITO[hashString(seed) % OKABE_ITO.length];
}
