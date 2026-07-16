<script lang="ts">
  interface Props {
    n: number;
    p?: number | null;
    ciLower?: number | null;
    ciUpper?: number | null;
    effectSize?: string | null;
    visible?: boolean;
    x?: number;
    y?: number;
  }

  let { n, p, ciLower, ciUpper, effectSize, visible = false, x = 0, y = 0 }: Props = $props();

  function sig(pVal: number): string {
    if (pVal < 0.001) return '***';
    if (pVal < 0.01) return '**';
    if (pVal < 0.05) return '*';
    return '';
  }
</script>

{#if visible}
  <div
    class="pointer-events-none fixed z-60 rounded-md border border-surface-200 bg-surface-0 px-3 py-2 text-xs shadow-md"
    style="left:{x + 12}px;top:{y - 8}px"
    role="tooltip"
  >
    <div class="flex items-center gap-2 text-surface-600 tabular-nums">
      <span class="font-medium text-surface-800">n={n}</span>
      {#if p != null}
        <span>p{p < 0.001 ? '<0.001' : '=' + p.toFixed(4)}</span>
        {#if sig(p)}
          <span class="text-primary-500">{sig(p)}</span>
        {/if}
      {/if}
      {#if ciLower != null && ciUpper != null}
        <span class="font-mono text-[11px] text-surface-400"
          >[{ciLower.toFixed(2)}, {ciUpper.toFixed(2)}]</span
        >
      {/if}
      {#if effectSize}
        <span class="text-surface-500">{effectSize}</span>
      {/if}
    </div>
  </div>
{/if}
