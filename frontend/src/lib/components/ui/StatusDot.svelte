<script lang="ts">
  interface Props {
    status?: 'active' | 'pending' | 'error' | 'unknown' | 'syncing';
    size?: 'sm' | 'md' | 'lg';
    class?: string;
  }

  let { status = 'active', size = 'sm', class: extraClass = '' }: Props = $props();

  const colors: Record<string, string> = {
    active: 'bg-success-500',
    pending: 'bg-warning-500',
    error: 'bg-error-500',
    unknown: 'bg-surface-400',
    syncing: 'bg-primary-500 animate-pulse'
  };

  const sizes: Record<string, string> = {
    sm: 'h-2 w-2',
    md: 'h-2.5 w-2.5',
    lg: 'h-3 w-3'
  };
</script>

<span
  class="inline-block rounded-full {colors[status]} {sizes[size]} {extraClass}"
  role="img"
  aria-label={status}
></span>
