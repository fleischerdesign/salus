<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  interface Props {
    label?: string;
    name?: string;
    value?: string;
    onchange?: (value: string) => void;
    required?: boolean;
    error?: string;
    hint?: string;
    disabled?: boolean;
    class?: string;
  }

  let {
    label,
    name,
    value = '',
    onchange,
    required = false,
    error,
    hint,
    disabled = false,
    class: extraClass = ''
  }: Props = $props();

  function handleInput(e: Event) {
    const input = e.target as HTMLInputElement;
    onchange?.(input.value);
  }

  let inputClass = $derived(
    'h-11 w-full rounded-lg border bg-surface-50 px-3 py-2.5 text-sm text-surface-900 transition-colors duration-micro placeholder:text-surface-400 hover:border-surface-400 focus:border-primary-500 focus:bg-surface-0 focus:outline-none focus:ring-2 focus:ring-primary-200 ' +
      (error ? 'border-error-400 bg-error-50' : 'border-surface-300') +
      (disabled ? ' opacity-50 cursor-not-allowed' : '')
  );
</script>

<div class="input {extraClass}">
  {#if label}
    <label
      for="{name ?? 'datepicker'}-input"
      class="mb-1 block text-[13px] font-semibold tracking-[0.05em] text-surface-900"
    >
      {label}{#if required}<span class="text-error-500"> *</span>{/if}
    </label>
  {/if}
  <input
    id="{name ?? 'datepicker'}-input"
    type="date"
    {name}
    {value}
    oninput={handleInput}
    {disabled}
    {required}
    class={inputClass}
  />
  {#if error}
    <span class="mt-1 flex items-center gap-1 text-sm text-error-600" role="alert">
      <Icon name="error" size="sm" />{error}
    </span>
  {/if}
  {#if hint && !error}
    <span class="mt-1 text-sm text-surface-500">{hint}</span>
  {/if}
</div>
