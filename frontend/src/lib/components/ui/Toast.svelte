<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { dismissToast, getToasts } from './toast-state.svelte';

  let toasts = $derived(getToasts());

  const iconMap: Record<string, string> = {
    success: 'check-circle',
    error: 'error',
    info: 'info',
    loading: 'sync',
    warning: 'warning',
  };

  const colorMap: Record<string, string> = {
    success: 'border-success-700',
    error: 'border-error-500',
    info: 'border-primary-500',
    loading: 'border-primary-500',
    warning: 'border-warning-700',
  };

  function fillPct(t: { progress?: boolean; progressValue?: number }): number | null {
    if (!t.progress || t.progressValue == null) return null;
    return Math.max(0, Math.min(1, t.progressValue)) * 100;
  }
</script>

{#if toasts.length > 0}
  <div
    class="fixed bottom-6 right-6 z-2000 flex flex-col gap-2 pointer-events-auto"
    role="region"
    aria-label="Notifications"
  >
    {#each toasts as t (t.id)}
      <div
        class="relative overflow-hidden flex items-center gap-3 min-w-[280px] max-w-[420px] rounded-lg border-l-4 bg-surface-0 px-4 py-3 shadow-lg animate-[slide-in_300ms_ease-out] {colorMap[t.type]}"
        role="alert"
      >
        {#if fillPct(t) !== null}
          <div
            class="absolute inset-0 origin-left bg-primary-500/10 transition-transform duration-500 ease-out"
            style="transform: scaleX({fillPct(t)! / 100})"
          ></div>
        {/if}

        <Icon
          name={iconMap[t.type]}
          size="md"
          class="relative z-10 shrink-0 text-surface-600 {t.type === 'loading' || t.progress ? 'animate-spin' : ''}"
        />

        <span class="relative z-10 flex-1 text-sm text-surface-900">{t.message}</span>

        {#if !t.progress}
          <button
            class="relative z-10 ml-2 flex h-4 w-4 shrink-0 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-surface-600"
            onclick={() => dismissToast(t.id)}
            aria-label="Dismiss"
          >
            <Icon name="close" size="sm" />
          </button>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  @keyframes slide-in {
    from {
      opacity: 0;
      transform: translateY(12px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
</style>
