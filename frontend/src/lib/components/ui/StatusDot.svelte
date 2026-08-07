<script lang="ts">
  interface Props {
    status?:
      | 'active'
      | 'success'
      | 'pending'
      | 'warning'
      | 'error'
      | 'critical'
      | 'info'
      | 'unknown'
      | 'syncing';
    size?: 'sm' | 'md' | 'lg';
    pulse?: boolean;
    class?: string;
  }

  let { status = 'active', size = 'sm', pulse = false, class: extraClass = '' }: Props = $props();

  const colors: Record<string, string> = {
    active: 'bg-success-500',
    success: 'bg-success-500',
    pending: 'bg-warning-500',
    warning: 'bg-warning-500',
    error: 'bg-error-500',
    critical: 'bg-error-500',
    info: 'bg-sky-500',
    unknown: 'bg-surface-400',
    syncing: 'bg-primary-500'
  };

  const sizes: Record<string, string> = {
    sm: 'h-2 w-2',
    md: 'h-2.5 w-2.5',
    lg: 'h-3 w-3'
  };

  let isPulsing = $derived(pulse || status === 'critical' || status === 'syncing');
</script>

{#if isPulsing}
  <span class="relative inline-flex {sizes[size]} {extraClass}">
    <span
      class="absolute inline-flex h-full w-full animate-ping rounded-full {colors[
        status
      ]} opacity-75"
    ></span>
    <span
      class="relative inline-flex h-full w-full rounded-full {colors[status]}"
      role="img"
      aria-label={status}
    ></span>
  </span>
{:else}
  <span
    class="inline-block rounded-full {colors[status] || colors.active} {sizes[size]} {extraClass}"
    role="img"
    aria-label={status}
  ></span>
{/if}
