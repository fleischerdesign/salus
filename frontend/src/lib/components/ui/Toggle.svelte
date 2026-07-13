<script lang="ts">
  interface Props {
    checked?: boolean;
    disabled?: boolean;
    label?: string;
    onchange?: (checked: boolean) => void;
    name?: string;
    class?: string;
  }

  let {
    checked = false,
    disabled = false,
    label,
    onchange,
    name,
    class: extraClass = ''
  }: Props = $props();

  function handleChange(e: Event) {
    const input = e.target as HTMLInputElement;
    onchange?.(input.checked);
  }

  let labelClass = $derived(
    'inline-flex items-center gap-3 ' + (disabled ? 'opacity-50' : 'cursor-pointer')
  );
  let trackClass = $derived(
    'relative inline-block h-6 w-11 rounded-full bg-surface-200 transition-colors duration-micro ' +
      (checked ? 'bg-primary-500' : '')
  );
  let thumbClass = $derived(
    'absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform duration-micro ' +
      (checked ? 'translate-x-5' : '')
  );
</script>

<label class="{labelClass} {extraClass}">
  {#if label}
    <span class="text-[13px] font-semibold tracking-[0.05em] text-surface-700">{label}</span>
  {/if}
  <span class={trackClass}>
    <span class={thumbClass}></span>
  </span>
  <input
    type="checkbox"
    {name}
    {checked}
    {disabled}
    onchange={handleChange}
    class="sr-only"
    role="switch"
    aria-checked={checked}
  />
</label>
