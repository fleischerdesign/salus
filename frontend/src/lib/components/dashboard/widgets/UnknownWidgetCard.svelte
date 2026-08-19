<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import type { DashboardWidget } from '$lib/types/widget-groups';

  interface Props {
    widget: DashboardWidget;
  }

  let { widget }: Props = $props();
</script>

<div
  class="flex h-full min-h-[140px] flex-col items-center justify-center space-y-1.5 rounded-3xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 text-center text-xs text-[var(--text-muted)] shadow-[var(--shadow-card)]"
>
  <div
    class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--bg-surface-100)] text-[var(--text-muted)]"
  >
    <Icon name="dashboard" size="md" />
  </div>
  <span class="font-bold text-[var(--text-main)]">{widget.title || 'Unbekanntes Widget'}</span>
  <span class="font-mono text-[0.625rem] text-[var(--text-muted)]">{widget.type}</span>
</div>
