<script lang="ts">
  import Icon from './Icon.svelte';

  let {
    value = $bindable(''),
    label = '',
    placeholder = '',
    type = 'text',
    unit = '',
    icon = '',
    error = '',
    hint = '',
    disabled = false,
    readonly = false,
    id = `input_${Math.random().toString(36).slice(2, 7)}`,
    oninput,
    onchange
  } = $props<{
    value?: string | number;
    label?: string;
    placeholder?: string;
    type?: 'text' | 'number' | 'email' | 'password' | 'search' | 'tel';
    unit?: string;
    icon?: string;
    error?: string;
    hint?: string;
    disabled?: boolean;
    readonly?: boolean;
    id?: string;
    oninput?: (e: Event) => void;
    onchange?: (e: Event) => void;
  }>();

  let isFocused = $state(false);
</script>

<div class="w-full space-y-1 text-xs">
  {#if label}
    <div class="flex items-center justify-between">
      <label for={id} class="font-bold text-[var(--text-muted)] block select-none">
        {label}
      </label>
      {#if unit && !isFocused}
        <span class="text-[0.625rem] text-[var(--text-soft)] font-bold tabular-nums">{unit}</span>
      {/if}
    </div>
  {/if}

  <div
    class="relative flex items-center rounded-2xl bg-[var(--bg-surface-50)] border transition-all duration-150 {isFocused ? 'border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/15 bg-[var(--bg-surface-0)] shadow-xs' : error ? 'border-rose-500 ring-2 ring-rose-500/15' : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]'} {disabled ? 'opacity-60 cursor-not-allowed bg-[var(--bg-surface-100)]' : ''}"
  >
    {#if icon}
      <div class="pl-3 text-[var(--text-soft)] shrink-0 flex items-center pointer-events-none">
        <Icon name={icon} size={15} />
      </div>
    {/if}

    <input
      {id}
      {type}
      bind:value
      {placeholder}
      {disabled}
      {readonly}
      onfocus={() => isFocused = true}
      onblur={() => isFocused = false}
      {oninput}
      {onchange}
      class="w-full bg-transparent px-3 py-2.5 text-xs text-[var(--text-main)] font-semibold placeholder:text-[var(--text-soft)] placeholder:font-normal outline-none {unit ? 'pr-12' : ''} {type === 'number' ? 'tabular-nums' : ''}"
    />

    {#if unit}
      <div class="absolute right-2.5 top-1/2 -translate-y-1/2 px-2 py-0.5 rounded-lg bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] text-[0.625rem] font-bold text-[var(--text-muted)] select-none tabular-nums pointer-events-none">
        {unit}
      </div>
    {/if}
  </div>

  {#if error}
    <p class="text-[0.6875rem] text-rose-500 font-bold mt-0.5 animate-[fadeIn_0.15s_ease-out]">{error}</p>
  {:else if hint}
    <p class="text-[0.6875rem] text-[var(--text-soft)] mt-0.5">{hint}</p>
  {/if}
</div>
