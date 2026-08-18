<script lang="ts">
  interface Props {
    label?: string;
    class?: string;
  }

  let { label, class: extraClass = '' }: Props = $props();
</script>

<div class="flex items-center gap-3 {extraClass}">
  <div class="flex-1" style="height: 1px; background: var(--color-surface-200)"></div>
  {#if label}
    <span class="text-surface-400 text-xs select-none">{label}</span>
    <div class="flex-1" style="height: 1px; background: var(--color-surface-200)"></div>
  {/if}
</div>
