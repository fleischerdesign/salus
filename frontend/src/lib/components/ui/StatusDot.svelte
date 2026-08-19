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
    size?: 'xs' | 'sm' | 'md' | 'lg';
    pulse?: boolean;
    class?: string;
  }

  let { status = 'active', size = 'sm', pulse = false, class: extraClass = '' }: Props = $props();

  const colors: Record<string, { solid: string; ping: string }> = {
    active: { solid: 'bg-emerald-500', ping: 'bg-emerald-400' },
    success: { solid: 'bg-emerald-500', ping: 'bg-emerald-400' },
    pending: { solid: 'bg-amber-500', ping: 'bg-amber-400' },
    warning: { solid: 'bg-amber-500', ping: 'bg-amber-400' },
    error: { solid: 'bg-rose-500', ping: 'bg-rose-400' },
    critical: { solid: 'bg-rose-500', ping: 'bg-rose-400' },
    info: { solid: 'bg-sky-500', ping: 'bg-sky-400' },
    unknown: { solid: 'bg-slate-400', ping: 'bg-slate-300' },
    syncing: { solid: 'bg-primary', ping: 'bg-blue-400' }
  };

  const sizes: Record<string, string> = {
    xs: 'h-1.5 w-1.5',
    sm: 'h-2 w-2',
    md: 'h-2.5 w-2.5',
    lg: 'h-3 w-3'
  };

  let colorScheme = $derived(colors[status] || colors.active);
  let isPulsing = $derived(pulse || status === 'critical' || status === 'syncing');
</script>

{#if isPulsing}
  <span class="relative inline-flex shrink-0 {sizes[size]} {extraClass}">
    <span
      class="absolute inline-flex h-full w-full animate-ping rounded-full {colorScheme.ping} opacity-75"
    ></span>
    <span
      class="relative inline-flex h-full w-full rounded-full {colorScheme.solid}"
      role="img"
      aria-label={status}
    ></span>
  </span>
{:else}
  <span
    class="inline-block shrink-0 rounded-full {colorScheme.solid} {sizes[size]} {extraClass}"
    role="img"
    aria-label={status}
  ></span>
{/if}
