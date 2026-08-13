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

/**
 * Resolves a categorical color for the active accessibility mode. When the
 * colorblind mode is off, returns the original color unchanged. When on,
 * returns a deterministic Okabe-Ito color derived from the stable `seed`, so
 * the same entity always maps to the same colorblind-safe color.
 */
export function resolveColor(seed: string, original: string): string {
  if (!theme.colorblind) return original;
  return OKABE_ITO[hashString(seed) % OKABE_ITO.length];
}
