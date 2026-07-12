<script lang="ts">
  interface Option {
    value: string;
    label: string;
  }

  interface Props {
    name: string;
    label?: string;
    options: Option[];
    value?: string;
    required?: boolean;
    class?: string;
  }

  let {
    name,
    label,
    options,
    value = $bindable(''),
    required = false,
    class: extraClass = ''
  }: Props = $props();
</script>

<div class="flex flex-col gap-1.5 {extraClass}">
  {#if label}
    <label for={name} class="text-sm font-medium text-surface-700">
      {label}
      {#if required}
        <span class="text-error-500 ml-0.5">*</span>
      {/if}
    </label>
  {/if}
  <select
    {name}
    id={name}
    bind:value
    {required}
    class="h-9 rounded-md border border-surface-300 bg-surface-50 px-3 text-sm text-surface-900 transition-colors duration-150 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-1 focus:ring-primary-500 focus:outline-none"
  >
    {#each options as opt}
      <option value={opt.value}>{opt.label}</option>
    {/each}
  </select>
</div>
