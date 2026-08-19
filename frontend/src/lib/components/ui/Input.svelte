<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import type { Snippet } from 'svelte';

  const baseInput =
    'h-10 w-full rounded-xl border px-3.5 py-2 text-sm font-semibold transition-colors duration-micro outline-none';
  const normalInput =
    'border-border-subtle bg-surface-0 text-text-main placeholder:text-text-muted/50 focus:border-primary';
  const errorInput = 'border-rose-500 bg-rose-500/5 text-text-main focus:border-rose-500';
  const disabledInput =
    'border-border-subtle bg-surface-100 text-text-muted cursor-not-allowed opacity-60';

  interface Props {
    name?: string;
    type?: string;
    label?: string;
    value?: string | number;
    required?: boolean;
    error?: string;
    hint?: string;
    placeholder?: string;
    autocomplete?: HTMLInputElement['autocomplete'];
    disabled?: boolean;
    readonly?: boolean;
    min?: number;
    max?: number;
    minlength?: number;
    step?: number | string;
    class?: string;
    style?: string;
    pattern?: string;
    el?: HTMLInputElement | null;
    id?: string;
    unit?: string;
    icon?: string;
    trailing?: Snippet;
    oninput?: (e: Event) => void;
    onchange?: (e: Event) => void;
    onkeydown?: (e: KeyboardEvent) => void;
    onkeyup?: (e: KeyboardEvent) => void;
    onfocus?: (e: FocusEvent) => void;
    onblur?: (e: FocusEvent) => void;
  }

  let {
    name = '',
    type = 'text',
    label = '',
    value = $bindable(''),
    required = false,
    error = '',
    hint = '',
    placeholder = '',
    disabled = false,
    readonly = false,
    min,
    max,
    minlength,
    step,
    class: extraClass = '',
    style,
    pattern,
    autocomplete,
    el = $bindable(null),
    id = name || `input_${Math.random().toString(36).slice(2, 7)}`,
    unit = '',
    icon = '',
    trailing,
    oninput,
    onchange,
    onkeydown,
    onkeyup,
    onfocus,
    onblur
  }: Props = $props();
</script>

<div class="space-y-1 {extraClass}" {style}>
  {#if label}
    <div class="flex items-center justify-between">
      <label
        for={id}
        class="block text-[0.6875rem] font-bold tracking-wider text-text-muted uppercase select-none"
      >
        {label}
        {#if required}<span class="ml-0.5 text-rose-500">*</span>{/if}
      </label>
      {#if unit}
        <span class="text-[0.625rem] font-bold text-text-muted tabular-nums">{unit}</span>
      {/if}
    </div>
  {/if}

  <div class="relative flex items-center">
    {#if icon}
      <div class="pointer-events-none flex shrink-0 items-center pl-3.5 text-text-muted">
        <Icon name={icon} size="sm" />
      </div>
    {/if}

    <input
      {id}
      name={name || id}
      {type}
      {autocomplete}
      {minlength}
      {min}
      {max}
      {step}
      {pattern}
      bind:value
      bind:this={el}
      {required}
      {placeholder}
      {disabled}
      {readonly}
      {oninput}
      {onchange}
      {onkeydown}
      {onkeyup}
      {onfocus}
      {onblur}
      class="{baseInput} {icon ? 'pl-10' : ''} {unit && !trailing ? 'pr-12' : ''} {trailing
        ? 'pr-11'
        : ''} {type === 'number' ? 'tabular-nums' : ''} {error ? errorInput : normalInput} {disabled
        ? disabledInput
        : ''}"
    />

    {#if unit && !trailing}
      <div
        class="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 rounded-lg border border-border-subtle bg-surface-100 px-2 py-0.5 text-[0.625rem] font-bold text-text-muted tabular-nums select-none"
      >
        {unit}
      </div>
    {/if}

    {#if trailing}
      <div class="absolute top-1/2 right-3.5 flex -translate-y-1/2 items-center">
        {@render trailing()}
      </div>
    {/if}
  </div>

  {#if error}
    <span class="mt-1 flex items-center gap-1 text-xs font-semibold text-rose-500" role="alert">
      <Icon name="error" size="sm" />
      {error}
    </span>
  {:else if hint}
    <span class="mt-1 block text-xs text-text-muted">{hint}</span>
  {/if}
</div>
