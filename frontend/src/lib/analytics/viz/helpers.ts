export function computeSparkline(values: number[]): string {
  if (values.length === 0 || Math.max(...values) === 0) {
    return '0,30 100,30';
  }
  const maxVal = Math.max(...values);
  const h = 26;
  const points: string[] = [];
  for (let i = 0; i < values.length; i++) {
    const x = (i / Math.max(values.length - 1, 1)) * 100;
    const y = h - (values[i] / maxVal) * h;
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return points.join(' ');
}

export function deltaStr(
  current: number | null,
  previous: number | null,
  opts: { unit?: string; isInteger?: boolean; upIsGood?: boolean } = {}
): string | null {
  if (current == null || previous == null || previous === 0) return null;
  const diff = current - previous;
  const diffStr = opts.isInteger ? `${Math.abs(diff)}` : Math.abs(diff).toFixed(1);
  const dir = diff > 0 ? '↑' : diff < 0 ? '↓' : '';
  return `${dir} ${diffStr}${opts.unit ?? ''}`;
}

export function yesterday(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00');
  d.setDate(d.getDate() - 1);
  return d.toISOString().slice(0, 10);
}

export function roundedSegments(
  stages: Array<{ label: string; value: number }>
): Array<{ label: string; pct: number }> {
  const total = stages.reduce((s, v) => s + v.value, 0);
  if (total <= 0) {
    return stages.map((s) => ({ label: s.label, pct: 0 }));
  }
  const raw = stages.map((s) => (s.value / total) * 100);
  const pcts = raw.map((r) => Math.round(r));
  let diff = 100 - pcts.reduce((s, v) => s + v, 0);
  if (diff !== 0) {
    const fractions = raw
      .map((r, i) => ({ frac: r - pcts[i], idx: i }))
      .sort((a, b) => (diff > 0 ? b.frac - a.frac : a.frac - b.frac));
    for (let k = 0; k < Math.abs(diff); k++) {
      pcts[fractions[k % fractions.length].idx] += diff > 0 ? 1 : -1;
    }
  }
  return stages.map((s, i) => ({ label: s.label, pct: pcts[i] }));
}
