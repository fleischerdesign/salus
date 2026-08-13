<script lang="ts">
  import Icon from './Icon.svelte';

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
    <label for={name} class="text-xs leading-[18px] font-semibold text-surface-900">
      {label}
      {#if required}
        <span class="ml-0.5 text-error-500">*</span>
      {/if}
    </label>
  {/if}
  <div class="relative flex items-center">
    <select
      {name}
      id={name}
      bind:value
      {required}
      class="duration-micro h-10 w-full appearance-none rounded-md border border-surface-300 bg-surface-50 pr-9 pl-3 text-sm font-normal text-surface-900 transition-colors hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-2 focus:ring-primary-200 focus:outline-none"
    >
      {#each options as opt}
        <option value={opt.value}>{opt.label}</option>
      {/each}
    </select>
    <span
      class="pointer-events-none absolute inset-y-0 right-0 flex w-9 items-center justify-center text-surface-400"
    >
      <Icon name="expand-more" size="sm" />
    </span>
  </div>
</div>
