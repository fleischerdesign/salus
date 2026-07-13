<script lang="ts">
  interface Props {
    total: number;
    current: number;
    class?: string;
  }

  let { total, current, class: extraClass = '' }: Props = $props();
</script>

<ol class="flex items-center gap-2 {extraClass}" role="list" aria-label="Progress">
  {#each Array(total) as _, i}
    {@const state = i < current ? 'completed' : i === current ? 'active' : 'pending'}
    <li>
      <span
        class="duration-micro flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold transition-colors
          {state === 'completed'
          ? 'bg-primary-500 text-white'
          : state === 'active'
            ? 'border-2 border-primary-500 bg-primary-50 text-primary-600'
            : 'bg-surface-100 text-surface-400'}"
        aria-current={state === 'active' ? 'step' : undefined}
        aria-label="Step {i + 1} of {total}"
      >
        {#if state === 'completed'}
          ✓
        {:else}
          {i + 1}
        {/if}
      </span>
    </li>
  {/each}
</ol>
