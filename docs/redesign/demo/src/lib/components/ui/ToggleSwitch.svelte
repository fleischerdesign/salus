<script lang="ts">
  let {
    checked = $bindable(false),
    label = '',
    description = '',
    disabled = false,
    id = `toggle_${Math.random().toString(36).slice(2, 7)}`,
    onchange
  } = $props<{
    checked?: boolean;
    label?: string;
    description?: string;
    disabled?: boolean;
    id?: string;
    onchange?: (checked: boolean) => void;
  }>();

  function toggle() {
    if (disabled) return;
    checked = !checked;
    onchange?.(checked);
  }
</script>

<div class="flex items-center justify-between gap-3 text-xs">
  {#if label || description}
    <div class="space-y-0.5 flex-1 select-none">
      {#if label}
        <label for={id} class="font-bold text-[var(--text-main)] block cursor-pointer">
          {label}
        </label>
      {/if}
      {#if description}
        <span class="text-[0.6875rem] text-[var(--text-muted)] block leading-snug">
          {description}
        </span>
      {/if}
    </div>
  {/if}

  <button
    type="button"
    {id}
    role="switch"
    aria-checked={checked}
    aria-label={label || 'Umschalten'}
    {disabled}
    onclick={toggle}
    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 {checked ? 'bg-[var(--color-primary)]' : 'bg-[var(--bg-surface-100)] border border-[var(--border-subtle)]'} {disabled ? 'opacity-50 cursor-not-allowed' : ''}"
  >
    <span
      class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {checked ? 'translate-x-5' : 'translate-x-0'}"
    ></span>
  </button>
</div>
