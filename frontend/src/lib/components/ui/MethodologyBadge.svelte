<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { type Snippet } from 'svelte';

  interface Citation {
    doi?: string | null;
    text: string;
  }

  interface Props {
    n: number;
    p?: number | null;
    effectSize?: string | null;
    ci95?: string | null;
    method: string;
    citation: Citation;
    children?: Snippet;
  }

  let { n, p, effectSize, ci95, method, citation, children }: Props = $props();

  let expanded = $state(false);

  function sigLevel(pVal: number): string {
    if (pVal < 0.001) return '***';
    if (pVal < 0.01) return '**';
    if (pVal < 0.05) return '*';
    return 'ns';
  }
</script>

<button
  class="group border-surface-200 bg-surface-50 text-surface-500 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-600 relative inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] transition-colors"
  onclick={() => (expanded = !expanded)}
  aria-expanded={expanded}
>
  <Icon name="science" size="sm" class="opacity-60" />
  <span>{method}</span>
  <span class="tabular-nums">n={n}</span>
  {#if p != null}
    <span class="tabular-nums">{sigLevel(p)}</span>
  {/if}
</button>

{#if expanded}
  <div
    class="border-surface-200 bg-surface-0 absolute z-50 mt-2 w-72 rounded-md border p-4 shadow-lg"
    role="dialog"
    aria-label="Methodology"
  >
    <div class="mb-3 flex items-center justify-between">
      <span class="text-surface-900 text-sm font-semibold">{method}</span>
      <button onclick={() => (expanded = false)} aria-label="Close">
        <Icon name="close" size="sm" class="text-surface-400" />
      </button>
    </div>
    <div class="text-surface-600 space-y-2 text-xs">
      <div class="flex justify-between">
        <span>Sample size</span>
        <span class="text-surface-800 font-medium tabular-nums">n = {n}</span>
      </div>
      {#if p != null}
        <div class="flex justify-between">
          <span>p-value (2-tailed)</span>
          <span class="text-surface-800 font-medium tabular-nums"
            >p = {p < 0.001 ? '<0.001' : p.toFixed(4)} {sigLevel(p)}</span
          >
        </div>
      {/if}
      {#if ci95}
        <div class="flex justify-between">
          <span>95% CI</span>
          <span class="text-surface-800 font-mono">{ci95}</span>
        </div>
      {/if}
      {#if effectSize}
        <div class="flex justify-between">
          <span>Effect size</span>
          <span class="text-surface-800 font-medium">{effectSize}</span>
        </div>
      {/if}
    </div>
    <div class="border-surface-100 text-surface-400 mt-3 border-t pt-2 text-[10px] leading-relaxed">
      {citation.text}
      {#if citation.doi}
        <a
          href="https://doi.org/{citation.doi}"
          target="_blank"
          rel="noopener"
          class="text-primary-500 ml-1 hover:underline">doi:{citation.doi}</a
        >
      {/if}
    </div>
    {#if children}
      <div class="mt-2">{@render children()}</div>
    {/if}
  </div>
  <button
    class="fixed inset-0 z-40 cursor-default"
    onclick={() => (expanded = false)}
    aria-hidden="true"
  ></button>
{/if}
