export function progressVariant(status: string): 'success' | 'error' | 'info' {
  if (status === 'fulfilled') return 'success';
  if (status === 'missed') return 'error';
  return 'info';
}

export function statusColor(status: string): string {
  if (status === 'fulfilled') return 'text-success-600';
  if (status === 'missed') return 'text-error-500';
  return 'text-primary-600';
}

export function formatValue(v: number | null | undefined): string {
  if (v === null || v === undefined) return '—';
  return v >= 1000
    ? v.toLocaleString(undefined, { maximumFractionDigits: 1 })
    : v.toFixed(1).replace(/\.0$/, '');
}
