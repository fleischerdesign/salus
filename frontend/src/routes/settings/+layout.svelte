<script lang="ts">
  import { type Snippet } from 'svelte';
  import { page } from '$app/state';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageTransition from '$components/ui/PageTransition.svelte';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();

  const tabs = [
    { key: 'account', label: 'Account', icon: 'person' },
    { key: 'privacy', label: 'Privacy', icon: 'shield' },
    { key: 'shares', label: 'Shares', icon: 'share' }
  ];

  let activeTab = $derived(
    tabs.find((t) => page.url.pathname === `/settings/${t.key}`)?.key ?? 'account'
  );
</script>

<svelte:head><title>Salus — Settings</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="Settings"
    subtitle="Configure account options, privacy limits, and active sharing keys."
    icon="settings"
    iconColor="#4f46e5"
  />

  <div class="flex gap-6">
    <nav class="flex w-60 shrink-0 flex-col border-r border-surface-200 py-2">
      {#each tabs as tab}
        <a
          href="/settings/{tab.key}"
          class="duration-micro flex cursor-pointer items-center gap-3 border-l-[3px] px-4 py-3 text-left text-[13px] font-semibold tracking-[0.05em] no-underline transition-colors {activeTab ===
          tab.key
            ? 'border-primary-500 bg-primary-50 text-primary-600'
            : 'border-transparent text-surface-600 hover:bg-surface-100'}"
        >
          {#if tab.icon}
            <Icon name={tab.icon} size="md" />
          {/if}
          {tab.label}
        </a>
      {/each}
    </nav>

    <div class="min-w-0 flex-1">
      <PageTransition>{@render children?.()}</PageTransition>
    </div>
  </div>
</div>
