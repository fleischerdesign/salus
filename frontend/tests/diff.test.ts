import { describe, it, expect } from 'vitest';
import { computeDiff, formatValue } from '$lib/utils/diff';

describe('computeDiff', () => {
  it('returns changed fields', () => {
    const client = { name: 'New', unit: 'kg', value: 100 };
    const server = { name: 'Old', unit: 'kg', value: 50 };
    const diff = computeDiff(client, server);
    expect(diff).toHaveLength(2);
    expect(diff.find((d) => d.field === 'name')?.client).toBe('New');
    expect(diff.find((d) => d.field === 'name')?.server).toBe('Old');
  });

  it('skips identical fields', () => {
    const client = { name: 'Same', unit: 'kg' };
    const server = { name: 'Same', unit: 'kg' };
    const diff = computeDiff(client, server);
    expect(diff).toHaveLength(0);
  });

  it('skips hidden fields', () => {
    const client = { name: 'X', password_hash: 'abc', token_hash: 'def', encrypted_key: 'key' };
    const server = { name: 'X', password_hash: 'xyz', token_hash: 'uvw', encrypted_key: 'new' };
    const diff = computeDiff(client, server);
    expect(diff).toHaveLength(0);
  });

  it('skips timestamp and id fields', () => {
    const client = {
      name: 'X',
      updated_at: '2025-01-01',
      created_at: '2025-01-01',
      deleted_at: '2025-01-01',
      id: 1,
      last_used_at: '2025-01-01'
    };
    const server = {
      name: 'X',
      updated_at: '2026-01-01',
      created_at: '2026-01-01',
      deleted_at: '2026-01-01',
      id: 2,
      last_used_at: '2026-01-01'
    };
    const diff = computeDiff(client, server);
    expect(diff).toHaveLength(0);
  });

  it('handles null and undefined values', () => {
    const client = { name: 'X', notes: null };
    const server = { name: 'X', notes: 'hello' };
    const diff = computeDiff(client, server);
    expect(diff).toHaveLength(1);
    expect(diff[0].client).toBe(null);
    expect(diff[0].server).toBe('hello');
  });
});

describe('formatValue', () => {
  it('formats null as em dash', () => {
    expect(formatValue(null)).toBe('\u2014');
    expect(formatValue(undefined)).toBe('\u2014');
  });

  it('formats booleans', () => {
    expect(formatValue(true)).toBe('Yes');
    expect(formatValue(false)).toBe('No');
  });

  it('formats numbers with locale', () => {
    const s = formatValue(1500);
    expect(s).toContain('1');
    expect(s).toContain('500');
  });

  it('formats ISO datetimes', () => {
    const s = formatValue('2025-06-15T12:30:00');
    expect(s).toContain('Jun');
    expect(s).toContain('15');
  });

  it('formats plain strings as-is', () => {
    expect(formatValue('hello')).toBe('hello');
  });

  it('formats objects as JSON', () => {
    const s = formatValue({ a: 1 });
    expect(s).toBe('{"a":1}');
  });
});
