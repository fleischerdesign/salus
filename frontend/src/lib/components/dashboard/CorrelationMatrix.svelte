<script lang="ts">
  import { slide } from 'svelte/transition';
  import Icon from '$components/ui/Icon.svelte';
  import MethodologyBadge from '$components/ui/MethodologyBadge.svelte';

  interface CorrPair {
    metric_a: string;
    metric_b: string;
    pearson_r: number;
    pearson_p: number;
    p_adjusted_bh: number;
    effect_size_d: number;
    ci_lower: number;
    ci_upper: number;
    n: number;
    interpretation: string;
  }

  interface Props {
    pairs: CorrPair[];
    nComparisons: number;
    correction: string;
    method?: 'pearson' | 'spearman';
  }

  let { pairs, nComparisons, correction, method = 'pearson' }: Props = $props();

  let selected: CorrPair | null = $state(null);

  function color(r: number): string {
    const t = (r + 1) / 2;
    if (t < 0.35)
      return `color-mix(in oklch, var(--color-error-600) ${(1 - t) * 200}%, var(--color-surface-100))`;
    if (t < 0.5)
      return `color-mix(in oklch, var(--color-surface-200) ${(0.5 - t) * 400}%, var(--color-surface-100))`;
    if (t > 0.65)
      return `color-mix(in oklch, var(--color-success-500) ${(t - 0.5) * 200}%, var(--color-surface-100))`;
    return 'var(--color-surface-100)';
  }

  let metrics = $derived([...new Set(pairs.flatMap((p) => [p.metric_a, p.metric_b]))]);

  function pair(a: string, b: string): CorrPair | undefined {
    return pairs.find(
      (p) => (p.metric_a === a && p.metric_b === b) || (p.metric_a === b && p.metric_b === a)
    );
  }
</script>

<div class="space-y-3">
  <div class="flex items-center gap-3">
    <MethodologyBadge
      n={metrics.length}
      method={method === 'pearson'
        ? 'Pearson r + Benjamini-Hochberg'
        : 'Spearman ρ + Benjamini-Hochberg'}
      citation={method === 'pearson'
        ? { text: 'Fisher 1915; Benjamini & Hochberg 1995' }
        : { text: 'Spearman 1904; Benjamini & Hochberg 1995' }}
    />
    <span class="text-[10px] text-[var(--text-soft)]">{nComparisons} Vergleiche · {correction}</span
    >
  </div>

  <div class="overflow-x-auto">
    <table class="w-full text-xs" role="grid" aria-label="Korrelationsmatrix">
      <thead>
        <tr>
          <th class="p-1"></th>
          {#each metrics as m}
            <th
              class="rotate-180 p-1 text-[0.6875rem] font-bold text-[var(--text-muted)] [writing-mode:vertical-lr]"
              >{m}</th
            >
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each metrics as ma}
          <tr>
            <td class="pr-2 text-right text-[0.6875rem] font-bold text-[var(--text-muted)]">{ma}</td
            >
            {#each metrics as mb}
              {@const p = pair(ma, mb)}
              <td
                class="cursor-pointer rounded-lg border border-[var(--border-subtle)] p-1 text-center tabular-nums transition-colors hover:ring-2 hover:ring-[var(--color-primary)]"
                class:opacity-40={!p || p.pearson_p >= 0.05}
                class:font-bold={p != null}
                style="background-color:{p ? color(p.pearson_r) : 'var(--bg-surface-50)'}"
                onclick={() => (selected = p ?? null)}
                role="gridcell"
              >
                {#if ma === mb}
                  <span class="text-[var(--text-soft)]">—</span>
                {:else if p}
                  {p.pearson_r.toFixed(2)}
                {:else}
                  <span class="text-[var(--text-soft)]">·</span>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if selected}
    <div
      class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] p-4 shadow-sm"
      transition:slide
    >
      <div class="mb-2 flex items-center justify-between">
        <span class="text-xs font-extrabold text-[var(--text-main)]">
          {selected.metric_a} ↔ {selected.metric_b}
        </span>
        <button
          class="flex h-6 w-6 cursor-pointer items-center justify-center rounded-full text-[var(--text-soft)] transition-colors hover:bg-[var(--bg-surface-100)] hover:text-[var(--text-main)]"
          onclick={() => (selected = null)}
          aria-label="Schließen"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>
      <div class="grid grid-cols-2 gap-2 text-xs text-[var(--text-muted)] sm:grid-cols-4">
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">Pearson r</span>
          <span class="font-mono font-bold text-[var(--text-main)]"
            >{selected.pearson_r.toFixed(4)}</span
          >
        </div>
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">p-Wert</span>
          <span class="font-mono font-bold text-[var(--text-main)]"
            >{selected.pearson_p < 0.001 ? '<0.001' : selected.pearson_p.toFixed(4)}</span
          >
        </div>
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">p (adj BH)</span>
          <span class="font-mono font-bold text-[var(--text-main)]"
            >{selected.p_adjusted_bh < 0.001 ? '<0.001*' : selected.p_adjusted_bh.toFixed(4)}</span
          >
        </div>
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">95% CI</span>
          <span class="font-mono font-bold text-[var(--text-main)]"
            >[{selected.ci_lower.toFixed(2)}, {selected.ci_upper.toFixed(2)}]</span
          >
        </div>
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">Effektstärke</span>
          <span class="font-bold text-[var(--text-main)] capitalize">{selected.interpretation}</span
          >
        </div>
        <div>
          <span class="block text-[0.6875rem] text-[var(--text-soft)]">Stichprobe</span>
          <span class="font-bold text-[var(--text-main)]">n = {selected.n}</span>
        </div>
      </div>
    </div>
  {/if}
</div>
