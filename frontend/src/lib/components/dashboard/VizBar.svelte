<script lang="ts">
  interface Segment {
    label: string;
    value: number;
    color: string;
  }

  interface Props {
    segments?: Segment[];
    total?: number;
    showLegend?: boolean;
  }

  let {
    segments = [],
    total,
    showLegend = true
  }: Props = $props();

  let computedTotal = $derived(total ?? segments.reduce((sum, s) => sum + s.value, 0));
</script>

<div class="flex flex-col gap-2">
  <div class="h-3 w-full overflow-hidden rounded-full bg-surface-100">
    <div class="flex h-full">
      {#each segments as segment}
        {#if computedTotal > 0}
          {@const pct = (segment.value / computedTotal) * 100}
          {@const barMinWidth = pct > 0 && pct < 4 ? 4 : pct}
          <div
            class="h-full first:rounded-l-full last:rounded-r-full"
            style="width: {barMinWidth}%; background-color: {segment.color}"
          ></div>
        {/if}
      {/each}
    </div>
  </div>

  {#if showLegend && segments.length > 0}
    <div class="flex flex-wrap gap-x-4 gap-y-1">
      {#each segments as segment}
        {#if computedTotal > 0}
          {@const pct = Math.round((segment.value / computedTotal) * 100)}
          <div class="flex items-center gap-1.5">
            <span
              class="inline-block h-2 w-2 rounded-full"
              style="background-color: {segment.color}"
            ></span>
            <span class="text-xs text-surface-500">{segment.label}</span>
            <span class="text-xs font-medium text-surface-700">{pct}%</span>
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>
