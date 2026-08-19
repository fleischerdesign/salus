<script lang="ts">
  import type { Snippet } from 'svelte';
  import Icon from '../ui/Icon.svelte';
  import Badge, { type BadgeVariant } from '../ui/Badge.svelte';
  import Spinner from '../ui/Spinner.svelte';

  interface Props {
    title: string;
    subtitle?: string;
    icon?: string;
    iconColor?: string;
    badgeText?: string;
    badgeVariant?: BadgeVariant;
    loading?: boolean;
    empty?: boolean;
    emptyText?: string;
    class?: string;
    children: Snippet;
    action?: Snippet;
    footer?: Snippet;
  }

  let {
    title,
    subtitle,
    icon,
    iconColor = 'var(--color-primary)',
    badgeText,
    badgeVariant = 'default',
    loading = false,
    empty = false,
    emptyText = 'Keine Daten für dieses Datum',
    class: className = '',
    children,
    action,
    footer
  }: Props = $props();
</script>

<div
  class="flex h-full flex-col justify-between space-y-4 rounded-3xl border border-border-subtle bg-surface-0 p-5 shadow-card transition-all hover:border-border-strong {className}"
>
  <!-- Header -->
  <div class="flex items-start justify-between gap-3">
    <div class="flex min-w-0 items-center gap-3">
      {#if icon}
        <div
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl shadow-2xs"
          style="background-color: color-mix(in srgb, {iconColor} 12%, transparent); color: {iconColor};"
        >
          <Icon name={icon} size="md" />
        </div>
      {/if}
      <div class="min-w-0">
        <h3 class="truncate text-sm font-extrabold tracking-tight text-text-main">
          {title}
        </h3>
        {#if subtitle}
          <p class="truncate text-xs text-text-muted">{subtitle}</p>
        {/if}
      </div>
    </div>

    <div class="flex shrink-0 items-center gap-2">
      {#if action}
        {@render action()}
      {/if}
      {#if badgeText}
        <Badge variant={badgeVariant} class="text-[0.625rem] font-bold">
          {badgeText}
        </Badge>
      {/if}
    </div>
  </div>

  <!-- Body Content -->
  <div class="flex-1">
    {#if loading}
      <div class="flex h-32 items-center justify-center py-6">
        <Spinner size="md" />
      </div>
    {:else if empty}
      <div
        class="flex h-28 flex-col items-center justify-center space-y-1 text-center text-xs text-text-muted"
      >
        <Icon name="info" size="sm" class="text-text-muted opacity-60" />
        <span>{emptyText}</span>
      </div>
    {:else}
      {@render children()}
    {/if}
  </div>

  <!-- Footer -->
  {#if footer}
    <div class="border-t border-border-subtle/60 pt-2.5 text-[0.6875rem] text-text-muted">
      {@render footer()}
    </div>
  {/if}
</div>
