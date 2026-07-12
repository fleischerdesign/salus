<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  interface ToastItem {
    id: number;
    message: string;
    type: 'success' | 'error' | 'info';
  }

  let toasts = $state<ToastItem[]>([]);
  let nextId = 0;

  function addToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const id = nextId++;
    toasts = [...toasts, { id, message, type }];
    setTimeout(() => {
      dismiss(id);
    }, 5000);
  }

  function dismiss(id: number) {
    toasts = toasts.filter(t => t.id !== id);
  }

  const iconMap: Record<string, string> = {
    success: 'check-circle',
    error: 'error',
    info: 'info',
  };

  const colorMap: Record<string, string> = {
    success: 'border-success-700',
    error: 'border-error-500',
    info: 'border-primary-500',
  };

  export function toast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    addToast(message, type);
  }
</script>

{#if toasts.length > 0}
  <div class="fixed bottom-6 right-6 z-2000 flex flex-col gap-2" role="region" aria-label="Notifications">
    {#each toasts as t (t.id)}
      <div
        class="flex items-center gap-3 rounded-lg border-l-4 bg-surface-0 px-4 py-3 shadow-lg animate-[slide-in_300ms_ease-out] {colorMap[t.type]}"
        role="alert"
      >
        <Icon name={iconMap[t.type]} size="md" class="text-surface-600" />
        <span class="text-sm text-surface-900">{t.message}</span>
        <button
          class="ml-2 flex h-4 w-4 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-surface-600"
          onclick={() => dismiss(t.id)}
          aria-label="Dismiss"
        >
          <Icon name="close" size="sm" />
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  @keyframes slide-in {
    from { opacity: 0; transform: translateY(12px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }
</style>
