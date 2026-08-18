<script lang="ts">
  import Icon from './Icon.svelte';

  interface Props {
    name?: string;
    label?: string;
    value?: string;
    placeholder?: string;
    required?: boolean;
    disabled?: boolean;
    rows?: number;
    error?: string;
    hint?: string;
    id?: string;
    class?: string;
    style?: string;
  }

  let {
    name = '',
    label = '',
    value = $bindable(''),
    placeholder = '',
    required = false,
    disabled = false,
    rows = 3,
    error,
    hint,
    id = name || `textarea_${Math.random().toString(36).slice(2, 7)}`,
    class: extraClass = '',
    style
  }: Props = $props();

  const baseClasses =
    'w-full rounded-xl border px-3.5 py-2.5 text-xs font-semibold transition-colors duration-micro outline-none resize-none';
  const normal =
    'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-main)] placeholder:text-[var(--text-muted)]/50 focus:border-[var(--color-primary)]';
  const errorClasses =
    'border-rose-500 bg-rose-500/5 text-[var(--text-main)] focus:border-rose-500';
  const disabledClasses =
    'border-[var(--border-subtle)] bg-[var(--bg-surface-100)] text-[var(--text-muted)] cursor-not-allowed opacity-60';
</script>

<div class="space-y-1 text-xs {extraClass}" {style}>
  {#if label}
    <label
      for={id}
      class="block text-[0.6875rem] font-bold tracking-wider text-[var(--text-muted)] uppercase select-none"
    >
      {label}
      {#if required}<span class="ml-0.5 text-rose-500">*</span>{/if}
    </label>
  {/if}
  <textarea
    {id}
    name={name || id}
    {rows}
    {placeholder}
    {required}
    {disabled}
    bind:value
    class="{baseClasses} {error ? errorClasses : normal} {disabled ? disabledClasses : ''}"
    aria-invalid={error ? 'true' : undefined}
  ></textarea>
  {#if error}
    <span class="mt-1 flex items-center gap-1 text-xs font-semibold text-rose-500" role="alert">
      <Icon name="error" size="sm" />
      {error}
    </span>
  {:else if hint}
    <span class="mt-1 block text-xs text-[var(--text-muted)]">{hint}</span>
  {/if}
</div>
