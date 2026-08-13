export const MS_PER_DAY = 86_400_000;

export function nowIso(): string {
  return new Date().toISOString();
}

export function dateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export function todayString(): string {
  return dateString(new Date());
}
