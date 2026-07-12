<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  const baseInput =
    'h-11 w-full rounded-md border px-3 py-2.5 text-sm text-surface-900 transition-colors duration-150 focus:outline-none focus:ring-2';
  const normalInput =
    'border-surface-300 bg-surface-50 placeholder:text-surface-400 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:ring-primary-200';
  const errorInput = 'border-error-400 bg-error-50 focus:border-error-500 focus:ring-error-200';
  const disabledInput = 'border-surface-200 bg-surface-100 text-surface-500 cursor-not-allowed';

  interface Props {
    name: string;
    type?: string;
    label?: string;
    value?: string | number;
    required?: boolean;
    error?: string;
    hint?: string;
    placeholder?: string;
    disabled?: boolean;
    min?: number;
    max?: number;
    minlength?: number;
    step?: number | string;
    class?: string;
    style?: string;
    pattern?: string;
    [key: string]: unknown;
  }

  let {
    name,
    type = 'text',
    label,
    value = $bindable(''),
    required = false,
    error,
    hint,
    placeholder,
    disabled = false,
    min,
    max,
    minlength,
    step,
    class: extraClass = '',
    style,
    pattern,
    ...restProps
  }: Props = $props();
</script>

<div class={extraClass} {style}>
  {#if label}
    <label for={name} class="text-[13px] leading-[18px] font-semibold text-surface-900">
      {label}
      {#if required}<span class="ml-0.5 text-error-500">*</span>{/if}
    </label>
  {/if}
  <div class="relative">
    <input
      id={name}
      {name}
      {type}
      {...restProps}
      {minlength}
      {min}
      {max}
      {step}
      {pattern}
      bind:value
      {required}
      {placeholder}
      {disabled}
      class="{baseInput} {error ? errorInput : normalInput} {disabled ? disabledInput : ''}"
    />
  </div>
  {#if error}
    <span class="flex items-center gap-1 text-sm text-error-600" role="alert">
      <Icon name="error" size="sm" />
      {error}
    </span>
  {:else if hint}
    <span class="text-sm text-surface-500">{hint}</span>
  {/if}
</div>
