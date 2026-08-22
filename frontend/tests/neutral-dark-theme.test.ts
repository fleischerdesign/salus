import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, it, expect } from 'vitest';

// Vitest is configured with css disabled (no styles injected into jsdom), so
// dark-mode token values are verified directly against the CSS source in
// src/app.css. The theme-level Tailwind tokens (--color-surface-*,
// --color-text-*, ...) resolve to the --bg-*/--text-* variables via the
// @theme mappings, so this contract covers the rendered values.
const css = readFileSync(fileURLToPath(new URL('../src/app.css', import.meta.url)), 'utf8');

// The dark-mode rule contains no nested braces, so the first "}" closes it.
const darkBlock = css.match(/\nhtml\.dark,[\s\S]*?\n\}/)?.[0] ?? '';

function token(name: string): string | undefined {
  const match = darkBlock.match(new RegExp(`--${name}:\\s*([^;]+);`));
  return match?.[1]?.trim();
}

function hexToRgb(hex: string): [number, number, number] {
  const value = hex.replace('#', '');
  return [0, 2, 4].map((i) => Number.parseInt(value.slice(i, i + 2), 16)) as [
    number,
    number,
    number
  ];
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex).map((c) => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrastRatio(a: string, b: string): number {
  const [lighter, darker] = [relativeLuminance(a), relativeLuminance(b)].sort((x, y) => y - x);
  return (lighter + 0.05) / (darker + 0.05);
}

describe('neutral dark mode tokens (app.css)', () => {
  it('defines the dark rule for html.dark and data-theme=dark', () => {
    expect(darkBlock).not.toBe('');
    expect(darkBlock).toMatch(/html\.dark,/);
    expect(darkBlock).toMatch(/\[data-theme='dark'\]/);
  });

  it('renders background surfaces on the pure neutral zinc ramp', () => {
    const ramp: Record<string, string> = {
      'bg-canvas': '#09090b',
      'bg-surface-0': '#121214',
      'bg-surface-50': '#18181b',
      'bg-surface-100': '#232326',
      'bg-surface-200': '#2e2e33',
      'bg-surface-300': '#3f3f46',
      'bg-surface-400': '#52525b',
      'bg-surface-500': '#71717a',
      'bg-surface-600': '#a1a1aa',
      'bg-surface-700': '#d4d4d8',
      'bg-surface-800': '#e4e4e7',
      'bg-surface-900': '#f4f4f5'
    };
    for (const [name, expected] of Object.entries(ramp)) {
      expect(token(name), `--${name}`).toBe(expected);
    }
  });

  it('keeps borders as clean neutral white overlays', () => {
    expect(token('border-subtle')).toBe('rgba(255, 255, 255, 0.08)');
    expect(token('border-strong')).toBe('rgba(255, 255, 255, 0.16)');
  });

  it('uses neutral typography and glass-dock tokens', () => {
    expect(token('text-main')).toBe('#fafafa');
    expect(token('text-muted')).toBe('#a1a1aa');
    expect(token('text-soft')).toBe('#71717a');
    expect(token('glass-dock-bg')).toBe('rgba(18, 18, 20, 0.85)');
  });

  it('keeps text WCAG AA readable on surface-0', () => {
    const surface = '#121214';
    expect(contrastRatio('#fafafa', surface)).toBeGreaterThanOrEqual(12);
    expect(contrastRatio('#a1a1aa', surface)).toBeGreaterThanOrEqual(4.5);
  });

  it('leaves no slate/blue-tinted values in the dark rule', () => {
    const oldSlate = [
      '#080c14',
      '#101624',
      '#172033',
      '#1f2b44',
      '#2b3956',
      '#334155',
      '#475569',
      '#64748b',
      '#94a3b8',
      '#cbd5e1',
      '#e2e8f0',
      '#f8fafc'
    ];
    for (const value of oldSlate) {
      expect(darkBlock, `dark rule must not contain ${value}`).not.toContain(value);
    }
  });

  it('preserves the dynamic OkLCH primary ramp in dark mode', () => {
    expect(token('color-primary')).toBe('oklch(0.7 0.19 var(--accent-hue))');
    expect(token('color-primary-soft')).toBe('oklch(0.3 0.08 var(--accent-hue) / 0.35)');
  });

  it('preserves domain colors unchanged in dark mode', () => {
    const domain: Record<string, string> = {
      'color-vital': '#ef4444',
      'color-activity': '#f97316',
      'color-hydrate': '#38bdf8',
      'color-fasting': '#a78bfa',
      'color-circadian': '#facc15',
      'color-sleep': '#818cf8',
      'color-success': '#10b981'
    };
    for (const [name, expected] of Object.entries(domain)) {
      expect(token(name), `--${name}`).toBe(expected);
    }
  });
});
