import { theme } from '$stores/theme.svelte';

// Okabe-Ito chromatic colors: a categorical palette distinguishable for
// protan/deutan/tritan vision (black is dropped — it is not a category color).
export const OKABE_ITO: readonly string[] = [
  '#0072B2', // blue
  '#E69F00', // orange
  '#009E73', // green
  '#D55E00', // vermillion
  '#CC79A7', // reddish purple
  '#56B4E9', // sky blue
  '#F0E442' // yellow
];

// Achromatic colors are neutral, never categorical — they pass through unchanged.
const NEUTRAL_COLORS = new Set([
  '#ffffff',
  '#fff',
  '#000000',
  '#000',
  '#9ca3af',
  '#6b7280',
  '#aaa9ad',
  '#64748b',
  '#f3f4f6',
  '#e5e7eb',
  '#d1d5db',
  '#f9fafb'
]);

interface HueEntry {
  color: string;
  hue: number;
}

function hexToHue(hex: string): number {
  const match = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!match) return 0;
  const r = parseInt(match[1].slice(0, 2), 16) / 255;
  const g = parseInt(match[1].slice(2, 4), 16) / 255;
  const b = parseInt(match[1].slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;
  if (delta === 0) return 0;

  let hue: number;
  if (max === r) hue = ((g - b) / delta) % 6;
  else if (max === g) hue = (b - r) / delta + 2;
  else hue = (r - g) / delta + 4;
  hue = Math.round(hue * 60);
  return hue < 0 ? hue + 360 : hue;
}

function hueDistance(a: number, b: number): number {
  const distance = Math.abs(a - b) % 360;
  return distance > 180 ? 360 - distance : distance;
}

const OKABE_HUES: readonly HueEntry[] = OKABE_ITO.map((color) => ({
  color,
  hue: hexToHue(color)
}));

/**
 * Resolves a categorical color for the active accessibility mode. When the
 * colorblind mode is off, or for achromatic colors, the original is returned
 * unchanged. When on, the original is mapped to the nearest Okabe-Ito color by
 * hue, preserving its warm/cool intent.
 */
export function resolveColor(original: string): string {
  const normalized = original.trim().toLowerCase();
  if (!theme.colorblind || NEUTRAL_COLORS.has(normalized)) return original;

  const hue = hexToHue(original);
  let best = OKABE_HUES[0];
  for (const entry of OKABE_HUES) {
    if (hueDistance(hue, entry.hue) < hueDistance(hue, best.hue)) best = entry;
  }
  return best.color;
}
