<script lang="ts">
  import Icon from './Icon.svelte';

  export interface SelectOptionItem {
    value: string | number;
    label: string;
    badge?: string;
    disabled?: boolean;
  }

  interface Props {
    name?: string;
    label?: string;
    options: (SelectOptionItem | { value: string; label: string })[];
    value?: string | number;
    required?: boolean;
    disabled?: boolean;
    icon?: string;
    error?: string;
    hint?: string;
    id?: string;
    class?: string;
    style?: string;
    onchange?: (val: string | number) => void;
  }

  let {
    name = '',
    label = '',
    options = [],
    value = $bindable(''),
    required = false,
    disabled = false,
    icon = '',
    error = '',
    hint = '',
    id = name || `select_${Math.random().toString(36).slice(2, 7)}`,
    class: extraClass = '',
    style,
    onchange
  }: Props = $props();

  let isFocused = $state(false);

  function handleChange(e: Event) {
    const val = (e.target as HTMLSelectElement).value;
    value = val;
    onchange?.(val);
  }
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

  <div
    class="relative flex items-center rounded-xl border bg-[var(--bg-surface-0)] transition-all duration-150 {isFocused
      ? 'border-[var(--color-primary)] shadow-xs ring-2 ring-[var(--color-primary)]/15'
      : error
        ? 'border-rose-500 ring-2 ring-rose-500/15'
        : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]'} {disabled
      ? 'cursor-not-allowed bg-[var(--bg-surface-100)] opacity-60'
      : ''}"
  >
    {#if icon}
      <div class="pointer-events-none flex shrink-0 items-center pl-3.5 text-[var(--text-muted)]">
        <Icon name={icon} size="sm" />
      </div>
    {/if}

    <select
      {id}
      name={name || id}
      {value}
      {disabled}
      {required}
      onchange={handleChange}
      onfocus={() => (isFocused = true)}
      onblur={() => (isFocused = false)}
      class="h-10 w-full cursor-pointer appearance-none bg-transparent pr-10 pl-3.5 text-xs font-semibold text-[var(--text-main)] outline-none [-moz-appearance:none] [-webkit-appearance:none] {icon
        ? 'pl-10'
        : ''}"
    >
      {#each options as opt}
        <option
          value={opt.value}
          disabled={'disabled' in opt ? opt.disabled : false}
          class="bg-[var(--bg-surface-0)] text-[var(--text-main)]"
        >
          {opt.label}
          {#if 'badge' in opt && opt.badge}({opt.badge}){/if}
        </option>
      {/each}
    </select>

    <!-- Sleek Custom Chevron with generous padding from the right border -->
    <div
      class="pointer-events-none absolute top-1/2 right-3.5 flex -translate-y-1/2 items-center justify-center text-[var(--text-muted)]"
    >
      <Icon name="keyboard-arrow-down" size="sm" />
    </div>
  </div>

  {#if error}
    <span class="mt-1 flex items-center gap-1 text-xs font-semibold text-rose-500" role="alert">
      <Icon name="error" size="sm" />
      {error}
    </span>
  {:else if hint}
    <span class="mt-1 block text-xs text-[var(--text-muted)]">{hint}</span>
  {/if}
</div>
