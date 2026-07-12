<script lang="ts">
  import Icon from './Icon.svelte';

  interface Props {
    name: string;
    label?: string;
    value?: string;
    placeholder?: string;
    required?: boolean;
    disabled?: boolean;
    rows?: number;
    error?: string;
    hint?: string;
    class?: string;
  }

  let {
    name,
    label,
    value = $bindable(''),
    placeholder = '',
    required = false,
    disabled = false,
    rows = 3,
    error,
    hint,
    class: extraClass = ''
  }: Props = $props();

  const baseClasses =
    'w-full rounded-md border px-3 py-2.5 text-sm text-surface-900 transition-colors duration-150 focus:outline-none focus:ring-2 resize-y min-h-[80px]';
  const normal =
    'border-surface-300 bg-surface-50 placeholder:text-surface-400 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-primary-200';
  const errorClasses = 'border-error-400 bg-error-50 focus:border-error-500 focus:ring-error-200';
  const disabledClasses = 'border-surface-200 bg-surface-100 text-surface-500 cursor-not-allowed';
</script>

<div class="flex flex-col gap-1 {extraClass}">
  {#if label}
    <label for={name} class="text-[13px] leading-[18px] font-semibold text-surface-900">
      {label}
      {#if required}<span class="ml-0.5 text-error-500">*</span>{/if}
    </label>
  {/if}
  <textarea
    id={name}
    {name}
    {rows}
    {placeholder}
    {required}
    {disabled}
    bind:value
    class="{baseClasses} {error ? errorClasses : normal} {disabled ? disabledClasses : ''}"
    aria-invalid={error ? 'true' : undefined}
  ></textarea>
  {#if error}
    <span class="flex items-center gap-1 text-sm text-error-600" role="alert">
      <Icon name="error" size="sm" />
      {error}
    </span>
  {:else if hint}
    <span class="text-sm text-surface-500">{hint}</span>
  {/if}
</div>
