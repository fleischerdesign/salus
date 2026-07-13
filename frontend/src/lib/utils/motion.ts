type EasingFn = (t: number) => number;

// ── Cubic-Bezier solver ──
function cubicBezier(x1: number, y1: number, x2: number, y2: number): EasingFn {
  return (t: number) => {
    if (t <= 0) return 0;
    if (t >= 1) return 1;
    let g = t;
    for (let i = 0; i < 8; i++) {
      const x = 3 * (1 - g) * (1 - g) * g * x1 + 3 * (1 - g) * g * g * x2 + g * g * g - t;
      if (Math.abs(x) < 1e-7) break;
      const dx = 3 * (1 - g) * (1 - g) * x1 + 6 * (1 - g) * g * (x2 - x1) + 3 * g * g * (1 - x2);
      if (Math.abs(dx) < 1e-7) break;
      g -= x / dx;
    }
    return 3 * (1 - g) * (1 - g) * g * y1 + 3 * (1 - g) * g * g * y2 + g * g * g;
  };
}

// ── Durations (mirror @theme --duration-*) ──
export const DURATIONS = {
  micro: 150,
  fast: 200,
  normal: 250,
  slow: 350
} as const;

// ── Easings (mirror @theme --ease-*) ──
export const EASINGS = {
  standard: cubicBezier(0.2, 0, 0, 1),
  out: cubicBezier(0, 0, 0.2, 1),
  in: cubicBezier(0.4, 0, 1, 1),
  inOut: cubicBezier(0.4, 0, 0.2, 1)
} as const;

// ── prefers-reduced-motion ──
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// ── Transition-param helper ──
export function motionParams(duration: number, easing?: EasingFn) {
  if (prefersReducedMotion()) return { duration: 0 };
  return easing ? { duration, easing } : { duration };
}

// ── Staggered fade-in for lists ──
export function staggerFade(i: number, baseDelay = 40, maxDelay = 300) {
  if (prefersReducedMotion()) return { duration: 0 };
  return { duration: DURATIONS.normal, delay: Math.min(i * baseDelay, maxDelay) };
}
