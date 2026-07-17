<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    checked?: boolean;
    disabled?: boolean;
    onchange?: (checked: boolean) => void;
    class?: string;
  }

  let {
    checked = false,
    disabled = false,
    onchange,
    class: extraClass = ''
  }: Props = $props();

  function handleClick(e: MouseEvent) {
    e.stopPropagation();
    if (disabled) return;
    onchange?.(!checked);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onchange?.(!checked);
    }
  }
</script>

<button
  type="button"
  class="duration-micro flex h-7 w-7 items-center justify-center rounded-full border-2 transition-all {checked
    ? 'border-primary-500 bg-primary-500'
    : 'border-surface-300 hover:border-primary-400'} {disabled
    ? 'cursor-not-allowed opacity-50'
    : 'cursor-pointer'} {extraClass}"
  onclick={handleClick}
  onkeydown={handleKeydown}
  {disabled}
  aria-pressed={checked}
>
  {#if checked}
    <Icon name="check" size="sm" class="text-white" />
  {/if}
</button>
