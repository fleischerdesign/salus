<script lang="ts">
  interface Props {
    size?: 'sm' | 'md' | 'lg';
  }

  let { size = 'md' }: Props = $props();

  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-[3px]'
  };
</script>

<div
  class={`animate-spin rounded-full border-surface-200 border-t-primary-600 ${sizeClasses[size]}`}
  role="status"
  aria-label="Loading"
></div>
