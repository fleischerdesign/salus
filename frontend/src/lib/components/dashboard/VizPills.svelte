<script lang="ts">
  interface PillItem {
    label: string;
    value: number;
    unit?: string;
    color?: string;
  }

  interface Props {
    items?: PillItem[];
  }

  let { items = [] }: Props = $props();
</script>

<div class="flex flex-wrap gap-2">
  {#each items as item}
    {@const pillColor = item.color ?? 'var(--color-primary-500)'}
    <div
      class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium"
      style="border-color: {pillColor}; color: {pillColor}; background-color: color-mix(in srgb, {pillColor} 8%, transparent)"
    >
      <span>{item.label}</span>
      <span class="opacity-70">{item.value}{item.unit ?? ''}</span>
    </div>
  {/each}
</div>
