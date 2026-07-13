<script lang="ts">
  import Icon from './Icon.svelte';
  import Btn from './Btn.svelte';
  import Modal from './Modal.svelte';

  interface Props {
    open?: boolean;
    title: string;
    variant?: 'danger' | 'warning' | 'info';
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    onconfirm?: () => void;
    oncancel?: () => void;
  }

  let {
    open = $bindable(false),
    title,
    variant = 'danger',
    message,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    onconfirm,
    oncancel
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
</script>

<Modal bind:open size="sm" {title} onclose={close}>
  <div class="flex flex-col items-center text-center">
    <Icon name={icons[variant]} size="2xl" class="mb-3 {iconColors[variant]}" />
    <p class="mt-2 text-sm text-surface-500">{message}</p>
  </div>
  <div class="mt-6 flex justify-center gap-3">
    <Btn variant="ghost" onclick={close}>{cancelLabel}</Btn>
    <Btn variant={variant === 'danger' ? 'danger' : 'primary'} onclick={confirm}>{confirmLabel}</Btn
    >
  </div>
</Modal>
