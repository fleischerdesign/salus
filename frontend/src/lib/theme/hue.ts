/**
 * Maps a pointer position to a hue (0–359). Angles run clockwise from the top
 * (12 o'clock), matching the conic gradient orientation.
 */
export function pointToHue(x: number, y: number, cx: number, cy: number): number {
  const dx = x - cx;
  const dy = y - cy;
  const angle = (Math.atan2(dx, -dy) * 180) / Math.PI;
  return Math.round((angle + 360) % 360) % 360;
}

/**
 * Builds a full-spectrum conic gradient using the same oklch hue ramp as the
 * accent, so the thumb always sits on the exact color the accent will take.
 */
export function hueGradient(): string {
  const stops: string[] = [];
  for (let hue = 0; hue < 360; hue += 30) {
    stops.push(`oklch(0.7 0.15 ${hue}) ${hue}deg`);
  }
  stops.push('oklch(0.7 0.15 0) 360deg');
  return `conic-gradient(from 0deg, ${stops.join(', ')})`;
}
