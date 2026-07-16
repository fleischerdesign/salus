<script lang="ts">
  interface Props {
    points: Array<{ x: number; lower: number; upper: number }>;
    color?: string;
    stroke?: string;
  }

  let {
    points,
    color = 'var(--color-primary-500)',
    stroke = 'var(--color-primary-300)'
  }: Props = $props();

  let d = $derived.by(() => {
    if (points.length < 2) return '';
    const upper = points.map((p) => `${p.x},${p.lower}`).join(' ');
    const lower = [...points]
      .reverse()
      .map((p) => `${p.x},${p.upper}`)
      .join(' ');
    return `M ${points[0].x},${points[0].lower} L ${upper} L ${lower} Z`;
  });
</script>

<g>
  <path {d} fill={color} opacity="0.12" stroke="none" />
  <polyline
    points={points.map((p) => `${p.x},${p.upper}`).join(' ')}
    fill="none"
    {stroke}
    stroke-width="1"
    stroke-dasharray="3 3"
    opacity="0.5"
  />
</g>
