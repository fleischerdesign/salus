<script lang="ts">
  interface Props {
    value?: number;
    max?: number;
    variant?: 'info' | 'success' | 'warning' | 'error';
    height?: 'sm' | 'md' | 'lg';
    label?: string;
    class?: string;
  }

  let {
    value = 0,
    max = 100,
    variant = 'info',
    height = 'md',
    label,
    class: extraClass = ''
  }: Props = $props();

  const pct = $derived(Math.min(100, Math.max(0, (value / max) * 100)));

  const heightClasses: Record<string, string> = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-4'
  };

  const variantClasses: Record<string, string> = {
    info: 'bg-primary-500',
    success: 'bg-success-700',
    warning: 'bg-warning-700',
    error: 'bg-error-500'
  };
</script>

{#if label}
  <div class="mb-1 text-xs font-medium text-surface-500">{label}</div>
{/if}
<div
  class="{heightClasses[height]} w-full overflow-hidden rounded-full bg-surface-100 {extraClass}"
>
  <div
    class="{heightClasses[
      height
    ]} duration-slow rounded-full transition-[width] ease-out {variantClasses[variant]}"
    style="width: {pct}%"
    role="progressbar"
    aria-valuenow={value}
    aria-valuemin="0"
    aria-valuemax={max}
  ></div>
</div>
