<script lang="ts">
  import { fly } from 'svelte/transition';
  import { DURATIONS, motionParams } from '$lib/utils/motion';
  import Icon from './Icon.svelte';

  interface Option {
    value: string;
    label: string;
  }

  interface Props {
    name?: string;
    label?: string;
    placeholder?: string;
    options: Option[];
    selected?: string[];
    required?: boolean;
    disabled?: boolean;
    hint?: string;
    error?: string;
    onchange?: (selected: string[]) => void;
    class?: string;
  }

  let {
    name = 'multiselect',
    label,
    placeholder = 'Select options…',
    options,
    selected = $bindable([]),
    required = false,
    disabled = false,
    hint,
    error,
    onchange,
    class: extraClass = ''
  }: Props = $props();

  let query = $state('');
  let open = $state(false);
  let inputRef: HTMLInputElement | null = null;

  let filtered = $derived(
    query ? options.filter((o) => o.label.toLowerCase().includes(query.toLowerCase())) : options
  );

  function toggle(value: string) {
    if (selected.includes(value)) {
      selected = selected.filter((v) => v !== value);
    } else {
      selected = [...selected, value];
    }
    onchange?.(selected);
  }

  function removeTag(value: string, e: MouseEvent) {
    e.stopPropagation();
    selected = selected.filter((v) => v !== value);
    onchange?.(selected);
  }

  const selectedLabels = $derived(
    selected.map((v) => options.find((o) => o.value === v)).filter(Boolean) as Option[]
  );

  const listboxId = `ms-listbox-${Math.random().toString(36).slice(2, 9)}`;
</script>

<div class="flex flex-col gap-1 {extraClass}">
  {#if label}
    <label for={name} class="text-[13px] font-semibold text-surface-900">
      {label}
      {#if required}<span class="ml-0.5 text-error-500">*</span>{/if}
    </label>
  {/if}

  <div class="relative">
    <div
      class="duration-micro flex min-h-11 flex-wrap items-center gap-1 rounded-md border border-surface-300 bg-surface-50 px-3 py-2 text-sm transition-colors focus-within:border-primary-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-primary-200 hover:border-surface-400 {disabled
        ? 'cursor-not-allowed opacity-50'
        : 'cursor-text'}"
      onclick={() => !disabled && ((open = true), inputRef?.focus())}
      onkeydown={(e: KeyboardEvent) => {
        if (e.key === 'Escape') open = false;
        else if (e.key === 'Enter' || e.key === 'ArrowDown') {
          open = true;
          inputRef?.focus();
        }
      }}
      role="combobox"
      aria-expanded={open}
      aria-controls={listboxId}
      tabindex="0"
    >
      {#each selectedLabels as opt}
        <span
          class="inline-flex items-center gap-1 rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700"
        >
          {opt.label}
          <button
            type="button"
            class="text-primary-500 hover:text-primary-700"
            aria-label="Remove {opt.label}"
            onclick={(e) => removeTag(opt.value, e)}
          >
            <Icon name="close" size="sm" />
          </button>
        </span>
      {/each}
      <input
        bind:this={inputRef}
        bind:value={query}
        {placeholder}
        {disabled}
        onfocus={() => (open = true)}
        onblur={() => setTimeout(() => (open = false), 150)}
        class="min-w-[80px] flex-1 bg-transparent text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none"
      />
    </div>

    {#if open && filtered.length > 0}
      <div
        id={listboxId}
        role="listbox"
        class="absolute top-full z-50 mt-1 max-h-48 w-full overflow-auto rounded-md border border-surface-200 bg-surface-0 py-1 shadow-lg"
        transition:fly={{ y: -4, ...motionParams(DURATIONS.micro) }}
      >
        {#each filtered as opt}
          {@const isSelected = selected.includes(opt.value)}
          <button
            type="button"
            class="duration-micro flex w-full items-center justify-between px-3 py-2 text-left text-sm transition-colors hover:bg-surface-50 {isSelected
              ? 'text-primary-600'
              : 'text-surface-700'}"
            onclick={() => toggle(opt.value)}
          >
            {opt.label}
            {#if isSelected}
              <Icon name="check" size="sm" class="text-primary-500" />
            {/if}
          </button>
        {/each}
      </div>
    {/if}
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
