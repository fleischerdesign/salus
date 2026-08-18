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
    class="divide-surface-200 flex min-h-[4rem] flex-col divide-y sm:flex-row sm:items-stretch sm:divide-x sm:divide-y-0"
  >
    <!-- Left Segment: Icon & Title -->
    <div class="flex flex-1 items-center gap-3 px-6 py-4">
      {#if backUrl}
        <a
          href={backUrl}
          class="duration-micro text-surface-400 hover:bg-surface-100 hover:text-surface-700 flex h-9 w-9 items-center justify-center rounded-lg transition-colors"
          aria-label="Go back"
        >
          <Icon name="arrow-back" size="sm" />
        </a>
      {/if}

      {#if icon}
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg font-bold"
          style="
            background-color: {iconBgColor
            ? iconBgColor
            : `color-mix(in oklch, ${iconColor || 'var(--color-primary-500)'} 12%, transparent)`};
            color: {iconColor || 'var(--color-primary-500)'};
          "
        >
          <Icon name={icon} />
        </div>
      {/if}

      <div class="min-w-0 flex-1">
        <h1 class="text-surface-900 truncate text-lg font-semibold">
          {title}
        </h1>
        {#if subtitle}
          <p class="text-surface-500 text-xs">{subtitle}</p>
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
    <div class="border-surface-100 border-t">
      {@render stats()}
    </div>
  {/if}
</Card>
