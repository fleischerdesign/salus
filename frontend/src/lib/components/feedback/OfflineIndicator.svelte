<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import { useOffline } from '$lib/db/use-offline.svelte';

  let showRestored = $state(false);
  let restoredTimer: ReturnType<typeof setTimeout> | null = null;
  let wasOffline = $state(!useOffline.isOnline);

  $effect(() => {
    if (useOffline.isOnline) {
      if (wasOffline) {
        showRestored = true;
        if (restoredTimer) clearTimeout(restoredTimer);
        restoredTimer = setTimeout(() => { showRestored = false; }, 3000);
      }
      wasOffline = false;
    } else {
      showRestored = false;
      wasOffline = true;
    }
  });
</script>

{#if useOffline.syncing}
  <div class="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-primary-500 px-4 py-2 text-sm font-medium text-white" role="status">
    <Icon name="sync" class="animate-spin" size="sm" />
    Syncing data...
  </div>
{:else if !useOffline.isOnline}
  <div class="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-warning-500 px-4 py-2 text-sm font-medium text-white" role="alert" aria-live="assertive">
    <Icon name="cloud-off" size="sm" />
    You are offline. Changes will sync when connection is restored.
    {#if useOffline.queueLength > 0}
      <span class="ml-1 rounded bg-white/20 px-1.5 py-0.5 text-xs">{useOffline.queueLength} pending</span>
    {/if}
  </div>
{:else if showRestored}
  <div class="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-success-500 px-4 py-2 text-sm font-medium text-white" role="alert" aria-live="polite">
    <Icon name="cloud-done" size="sm" />
    {#if useOffline.queueLength > 0}
      Syncing {useOffline.queueLength} pending change{useOffline.queueLength > 1 ? 's' : ''}...
    {:else}
      Connection restored.
    {/if}
  </div>
{/if}

{#if useOffline.syncError}
  <div class="fixed bottom-10 left-0 right-0 z-50 flex items-center justify-center gap-2 bg-error-500 px-4 py-2 text-sm font-medium text-white" role="alert">
    <Icon name="error" size="sm" />
    {useOffline.syncError}
  </div>
{/if}
