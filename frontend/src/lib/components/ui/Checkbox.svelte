<script lang="ts">
  interface Props {
    name?: string;
    label?: string;
    checked?: boolean;
    disabled?: boolean;
    id?: string;
    class?: string;
    onchange?: (checked: boolean) => void;
  }

  let {
    name = '',
    label = '',
    checked = $bindable(false),
    disabled = false,
    id = name || `chk_${Math.random().toString(36).slice(2, 7)}`,
    class: extraClass = '',
    onchange
  }: Props = $props();

  function handleChange(e: Event) {
    const input = e.target as HTMLInputElement;
    checked = input.checked;
    onchange?.(input.checked);
  }
</script>

<label
  class="inline-flex cursor-pointer items-center gap-2 select-none {disabled
    ? 'cursor-not-allowed opacity-50'
    : ''} {extraClass}"
>
  <input
    {id}
    type="checkbox"
    name={name || id}
    bind:checked
    {disabled}
    onchange={handleChange}
    class="h-4 w-4 cursor-pointer rounded-md border border-border-subtle bg-surface-0 accent-primary focus:ring-1 focus:ring-primary"
  />
  {#if label}
    <span class="text-xs font-semibold text-text-main">{label}</span>
  {/if}
</label>
