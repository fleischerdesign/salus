<script lang="ts">
  import { type Snippet } from 'svelte';
  import { page } from '$app/state';
  import Icon from '$components/ui/Icon.svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();

  const tabs = [
    { key: 'general', label: 'General', icon: 'settings' },
    { key: 'users', label: 'Users', icon: 'groups' },
    { key: 'stats', label: 'Statistics', icon: 'monitoring' },
    { key: 'plugins', label: 'Plugins', icon: 'extension' },
    { key: 'backups', label: 'Backups', icon: 'cloud-done' },
  ];

  let activeTab = $derived(
    tabs.find((t) => page.url.pathname === `/admin/${t.key}`)?.key ?? 'stats'
  );
</script>

<svelte:head><title>Salus — Admin</title></svelte:head>

<div class="space-y-6">
  <h1 class="text-2xl font-semibold text-surface-900">Admin Panel</h1>

  <div class="flex gap-6">
    <nav class="flex w-60 shrink-0 flex-col border-r border-surface-200 py-2">
      {#each tabs as tab}
        <a
          href="/admin/{tab.key}"
          class="flex cursor-pointer items-center gap-3 border-l-[3px] px-4 py-3 text-left text-[13px] font-semibold tracking-[0.05em] no-underline transition-colors duration-150 {activeTab === tab.key ? 'border-primary-500 bg-primary-50 text-primary-600' : 'border-transparent text-surface-600 hover:bg-surface-100'}"
        >
          <Icon name={tab.icon} size="md" />
          {tab.label}
        </a>
      {/each}
    </nav>

    <div class="min-w-0 flex-1">
      {@render children?.()}
    </div>
  </div>
</div>
