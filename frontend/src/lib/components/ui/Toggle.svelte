<script lang="ts">
  let {
    checked = $bindable(false),
    label = '',
    description = '',
    disabled = false,
    id = `toggle_${Math.random().toString(36).slice(2, 7)}`,
    name = '',
    class: extraClass = '',
    onchange
  } = $props<{
    checked?: boolean;
    label?: string;
    description?: string;
    disabled?: boolean;
    id?: string;
    name?: string;
    class?: string;
    onchange?: (checked: boolean) => void;
  }>();

  function toggle() {
    if (disabled) return;
    checked = !checked;
    onchange?.(checked);
  }
</script>

<div class="flex items-center justify-between gap-3 text-xs {extraClass}">
  {#if label || description}
    <div class="flex-1 space-y-0.5 select-none">
      {#if label}
        <label for={id} class="block cursor-pointer font-bold text-[var(--text-main)]">
          {label}
        </label>
      {/if}
      {#if description}
        <span class="block text-[0.6875rem] leading-snug text-[var(--text-muted)]">
          {description}
        </span>
      {/if}
    </div>
  {/if}

  <button
    type="button"
    {id}
    name={name || id}
    role="switch"
    aria-checked={checked}
    aria-label={label || 'Umschalten'}
    {disabled}
    onclick={toggle}
    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:outline-none {checked
      ? 'bg-[var(--color-primary)]'
      : 'border border-[var(--border-subtle)] bg-[var(--bg-surface-100)]'} {disabled
      ? 'cursor-not-allowed opacity-50'
      : ''}"
  >
    <span
      class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {checked
        ? 'translate-x-5'
        : 'translate-x-0'}"
    ></span>
  </button>
</div>
