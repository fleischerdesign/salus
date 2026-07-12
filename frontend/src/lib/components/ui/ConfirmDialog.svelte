<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from './Icon.svelte';
  import Btn from './Btn.svelte';

  interface Props {
    open?: boolean;
    title: string;
    variant?: 'danger' | 'warning' | 'info';
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    onconfirm?: () => void;
    oncancel?: () => void;
    class?: string;
  }

  let {
    open = $bindable(false),
    title,
    variant = 'danger',
    message,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    onconfirm,
    oncancel,
    class: extraClass = ''
  }: Props = $props();

  const icons: Record<string, string> = {
    danger: 'warning',
    warning: 'warning',
    info: 'info'
  };

  const iconColors: Record<string, string> = {
    danger: 'text-error-500',
    warning: 'text-warning-500',
    info: 'text-primary-500'
  };

  function close() {
    open = false;
    oncancel?.();
  }

  function confirm() {
    open = false;
    onconfirm?.();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }

  function onBackdrop(e: MouseEvent) {
    if (e.target === e.currentTarget) close();
  }
</script>

<svelte:window onkeydown={onKeydown} />

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    onclick={onBackdrop}
    role="presentation"
  >
    <div class="relative z-10 mx-4 w-full max-w-sm rounded-lg bg-surface-0 p-6 shadow-lg {extraClass}" role="dialog" aria-modal="true" aria-label={title}>
      <div class="flex flex-col items-center text-center">
        <Icon name={icons[variant]} size="2xl" class="mb-3 {iconColors[variant]}" />
        <h2 class="text-lg font-semibold text-surface-900">{title}</h2>
        <p class="mt-2 text-sm text-surface-500">{message}</p>
      </div>
      <div class="mt-6 flex justify-center gap-3">
        <Btn variant="ghost" onclick={close}>{cancelLabel}</Btn>
        <Btn variant={variant === 'danger' ? 'danger' : 'primary'} onclick={confirm}>{confirmLabel}</Btn>
      </div>
    </div>
  </div>
{/if}
