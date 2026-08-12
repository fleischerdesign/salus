export const MS_PER_DAY = 86_400_000;

export function nowIso(): string {
  return new Date().toISOString();
}
