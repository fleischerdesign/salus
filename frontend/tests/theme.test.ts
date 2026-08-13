import { describe, it, expect, beforeEach } from 'vitest';
import { theme } from '$stores/theme.svelte';

describe('theme', () => {
  beforeEach(() => {
    localStorage.clear();
    theme.setMode('system');
    theme.setColorblind(false);
  });

  it('defaults to system', () => {
    expect(theme.mode).toBe('system');
  });

  it('resolves system to light without dark preference', () => {
    expect(theme.resolved).toBe('light');
  });

  it('resolves explicit dark', () => {
    theme.setMode('dark');
    expect(theme.resolved).toBe('dark');
  });

  it('persists mode', () => {
    theme.setMode('dark');
    expect(localStorage.getItem('salus_theme')).toBe('dark');
  });

  it('persists colorblind flag', () => {
    theme.setColorblind(true);
    expect(theme.colorblind).toBe(true);
    expect(localStorage.getItem('salus_colorblind')).toBe('true');
  });
});
