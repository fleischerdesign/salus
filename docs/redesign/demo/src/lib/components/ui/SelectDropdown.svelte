<script lang="ts">
  import Icon from './Icon.svelte';

  interface OptionItem {
    value: string | number;
    label: string;
    badge?: string;
    disabled?: boolean;
  }

  let {
    value = $bindable(''),
    label = '',
    options = [],
    icon = '',
    disabled = false,
    id = `select_${Math.random().toString(36).slice(2, 7)}`,
    onchange
  } = $props<{
    value?: string | number;
    label?: string;
    options: OptionItem[];
    icon?: string;
    disabled?: boolean;
    id?: string;
    onchange?: (val: string | number) => void;
  }>();

  let isFocused = $state(false);

  function handleChange(e: Event) {
    const val = (e.target as HTMLSelectElement).value;
    value = val;
    onchange?.(val);
  }
</script>

<div class="w-full space-y-1 text-xs">
  {#if label}
    <label for={id} class="font-bold text-[var(--text-muted)] block select-none">
      {label}
    </label>
  {/if}

  <div
    class="relative flex items-center rounded-2xl bg-[var(--bg-surface-50)] border transition-all duration-150 {isFocused ? 'border-[var(--color-primary)] ring-2 ring-[var(--color-primary)]/15 bg-[var(--bg-surface-0)] shadow-xs' : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]'} {disabled ? 'opacity-60 cursor-not-allowed bg-[var(--bg-surface-100)]' : ''}"
  >
    {#if icon}
      <div class="pl-3 text-[var(--text-soft)] shrink-0 flex items-center pointer-events-none">
        <Icon name={icon} size={15} />
      </div>
    {/if}

    <select
      {id}
      {value}
      {disabled}
      onchange={handleChange}
      onfocus={() => isFocused = true}
      onblur={() => isFocused = false}
      class="w-full bg-transparent px-3 py-2.5 pr-8 text-xs text-[var(--text-main)] font-semibold outline-none cursor-pointer appearance-none {icon ? 'pl-2' : ''}"
    >
      {#each options as opt}
        <option value={opt.value} disabled={opt.disabled} class="bg-[var(--bg-surface-0)] text-[var(--text-main)]">
          {opt.label} {#if opt.badge}({opt.badge}){/if}
        </option>
      {/each}
    </select>

    <!-- Sleek Custom Chevron -->
    <div class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-soft)] pointer-events-none">
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
  </div>
</div>
