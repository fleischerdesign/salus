<script lang="ts">
  import { type Snippet } from 'svelte';
  import Icon from './Icon.svelte';

  interface Props {
    primary?: string;
    secondary?: string;
    icon?: string;
    iconColor?: string;
    action?: Snippet;
    children?: Snippet;
    clickable?: boolean;
    hoverable?: boolean;
    href?: string;
    divider?: boolean;
    class?: string;
  }

  let {
    primary,
    secondary,
    icon,
    iconColor,
    action,
    children,
    clickable = false,
    hoverable = false,
    href,
    divider = true,
    class: extraClass = ''
  }: Props = $props();

  let tag = $derived(href ? 'a' : 'div');
  let interactive = $derived(clickable || hoverable || href !== undefined);
</script>

{#snippet defaultBody()}
  {#if icon}
    <Icon
      name={icon}
      class="text-surface-400"
      style={iconColor ? `color: ${iconColor}` : undefined}
    />
  {/if}
  <div class="min-w-0 flex-1">
    {#if children}
      {@render children()}
    {:else}
      <p class="truncate text-sm font-medium text-surface-900">{primary}</p>
      {#if secondary}
        <p class="mt-0.5 truncate text-xs text-surface-500">{secondary}</p>
      {/if}
    {/if}
  </div>
{/snippet}

{#if tag === 'a'}
  <a
    {href}
    class="group flex items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-surface-50 {divider
      ? 'border-b border-surface-100 last:border-b-0'
      : ''} {extraClass}"
  >
    {@render defaultBody()}
    {#if action}
      <div class="flex-shrink-0">
        {@render action()}
      </div>
    {/if}
  </a>
{:else}
  <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
  <div
    class="group flex items-center gap-3 px-4 py-3 transition-colors duration-150 {interactive
      ? 'cursor-pointer hover:bg-surface-50'
      : ''} {divider ? 'border-b border-surface-100 last:border-b-0' : ''} {extraClass}"
    role={interactive ? 'button' : undefined}
    tabindex={interactive ? 0 : undefined}
    onkeydown={interactive
      ? (e: KeyboardEvent) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
          }
        }
      : undefined}
  >
    {@render defaultBody()}
    {#if action}
      <div class="flex-shrink-0">
        {@render action()}
      </div>
    {/if}
  </div>
{/if}
