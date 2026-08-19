<script lang="ts">
  import { getWidgetManifest } from '$lib/dashboard/widget-registry';
  import type { DashboardWidget } from '$lib/types/widget-groups';
  import UnknownWidgetCard from './widgets/UnknownWidgetCard.svelte';
  import { todayString } from '$lib/utils/datetime';

  interface Props {
    widget: DashboardWidget;
    date?: string;
    waterAmount?: number;
    liveMetrics?: Map<string, number>;
    onopenfasting?: () => void;
    onopen?: (route: string) => void;
  }

  let { widget, date = todayString(), onopenfasting, onopen }: Props = $props();

  const manifest = $derived(getWidgetManifest(widget.type));

  function handleOpen(route: string) {
    if (route === '/fasting') {
      onopenfasting?.();
    }
    onopen?.(route);
  }
</script>

<div class="h-full">
  {#if manifest}
    <manifest.component {date} onopen={handleOpen} />
  {:else}
    <UnknownWidgetCard {widget} />
  {/if}
</div>
