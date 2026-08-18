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
  class="border-surface-200 bg-surface-50 flex items-center gap-3 rounded-lg border px-3 py-3"
  role="status"
>
  <Icon name="info" size="sm" class="text-surface-400 flex-shrink-0" />
  <div class="min-w-0 flex-1">
    <p class="text-surface-700 text-sm">
      Barcode <span class="text-surface-800 font-mono text-xs font-medium">{barcode}</span> isn't in the
      database yet.
    </p>
    <p class="text-surface-400 mt-0.5 text-xs">
      Add the nutrition info once — the next scan will recognize it.
    </p>
  </div>
  <Btn variant="primary" size="sm" onclick={onCreate}>Create food</Btn>
  {#if onDismiss}
    <button
      type="button"
      class="text-surface-400 hover:bg-surface-100 hover:text-surface-600 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded transition-colors"
      aria-label="Dismiss"
      onclick={onDismiss}
    >
      <Icon name="close" size="sm" />
    </button>
  {/if}
</div>
