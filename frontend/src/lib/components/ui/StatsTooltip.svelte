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
    class="border-surface-200 bg-surface-0 pointer-events-none fixed z-60 rounded-md border px-3 py-2 text-xs shadow-md"
    style="left:{x + 12}px;top:{y - 8}px"
    role="tooltip"
  >
    <div class="text-surface-600 flex items-center gap-2 tabular-nums">
      <span class="text-surface-800 font-medium">n={n}</span>
      {#if p != null}
        <span>p{p < 0.001 ? '<0.001' : '=' + p.toFixed(4)}</span>
        {#if sig(p)}
          <span class="text-primary-500">{sig(p)}</span>
        {/if}
      {/if}
      {#if ciLower != null && ciUpper != null}
        <span class="text-surface-400 font-mono text-[10px]"
          >[{ciLower.toFixed(2)}, {ciUpper.toFixed(2)}]</span
        >
      {/if}
      {#if effectSize}
        <span class="text-surface-500">{effectSize}</span>
      {/if}
    </div>
  </div>
{/if}
