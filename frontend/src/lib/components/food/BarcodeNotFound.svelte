<script lang="ts">
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    barcode: string;
    onCreate: () => void;
    onDismiss?: () => void;
  }

  let { barcode, onCreate, onDismiss }: Props = $props();
</script>

<div
  class="flex items-center gap-3 rounded-lg border border-surface-200 bg-surface-50 px-3 py-3"
  role="status"
>
  <Icon name="info" size="sm" class="flex-shrink-0 text-surface-400" />
  <div class="min-w-0 flex-1">
    <p class="text-sm text-surface-700">
      Barcode <span class="font-mono text-xs font-medium text-surface-800">{barcode}</span> isn't in the
      database yet.
    </p>
    <p class="mt-0.5 text-xs text-surface-400">
      Add the nutrition info once — the next scan will recognize it.
    </p>
  </div>
  <Btn variant="primary" size="sm" onclick={onCreate}>Create food</Btn>
  {#if onDismiss}
    <button
      type="button"
      class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600"
      aria-label="Dismiss"
      onclick={onDismiss}
    >
      <Icon name="close" size="sm" />
    </button>
  {/if}
</div>
