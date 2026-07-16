<script lang="ts">
  import Card from './Card.svelte';
  import Icon from './Icon.svelte';
  import type { Snippet } from 'svelte';

  interface Props {
    title: string;
    subtitle?: string;
    backUrl?: string;
    icon?: string;
    iconColor?: string;
    iconBgColor?: string;
    actions?: Snippet;
    stats?: Snippet;
  }

  let { title, subtitle, backUrl, icon, iconColor, iconBgColor, actions, stats }: Props = $props();
</script>

<Card padding={false} class="overflow-hidden">
  <div
    class="flex min-h-[4rem] flex-col divide-y divide-surface-200 sm:flex-row sm:items-stretch sm:divide-x sm:divide-y-0"
  >
    <!-- Left Segment: Icon & Title -->
    <div class="flex flex-1 items-center gap-3 px-6 py-4">
      {#if backUrl}
        <a
          href={backUrl}
          class="duration-micro flex h-9 w-9 items-center justify-center rounded-lg text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700"
          aria-label="Go back"
        >
          <Icon name="arrow-back" size="sm" />
        </a>
      {/if}

      {#if icon}
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg font-bold"
          style="
            background-color: {iconBgColor ? iconBgColor : `${iconColor || '#4f46e5'}20`};
            color: {iconColor || '#4f46e5'};
          "
        >
          <Icon name={icon} />
        </div>
      {/if}

      <div class="min-w-0 flex-1">
        <h1 class="truncate text-lg font-semibold text-surface-900">
          {title}
        </h1>
        {#if subtitle}
          <p class="text-xs text-surface-500">{subtitle}</p>
        {/if}
      </div>
    </div>

    <!-- Right Segment: Actions -->
    {#if actions}
      <div class="flex items-stretch">
        {@render actions()}
      </div>
    {/if}
  </div>

  {#if stats}
    <div class="border-t border-surface-100">
      {@render stats()}
    </div>
  {/if}
</Card>
