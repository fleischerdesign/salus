<script lang="ts">
  import { type Snippet } from 'svelte';
  import { page } from '$app/state';
  import Badge from '$components/ui/Badge.svelte';

  interface Props {
    children?: Snippet;
  }

  let { children }: Props = $props();

  const navigationTabs = [
    { id: 'overview', label: 'Übersicht & Jobs', path: '/admin' },
    { id: 'general', label: 'Allgemein & Config', path: '/admin/general' },
    { id: 'users', label: 'Benutzer', path: '/admin/users' },
    { id: 'stats', label: 'Statistiken', path: '/admin/stats' },
    { id: 'foods', label: 'Lebensmittel-DB', path: '/admin/foods' },
    { id: 'plugins', label: 'Erweiterungen', path: '/admin/plugins' },
    { id: 'backups', label: 'Backups', path: '/admin/backups' }
  ];

  let activeTab = $derived(
    page.url.pathname === '/admin'
      ? 'overview'
      : (navigationTabs.find((t) => t.path !== '/admin' && page.url.pathname.startsWith(t.path))
          ?.id ?? 'overview')
  );
</script>

<svelte:head><title>Salus — Administration</title></svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <div class="flex items-center gap-2">
        <h1 class="text-2xl font-extrabold tracking-tight">System- und Server-Administration</h1>
        <Badge variant="primary" class="font-bold">Admin-Modus</Badge>
      </div>
      <p class="mt-0.5 text-sm text-text-muted">
        Server-Ressourcen, AppScheduler Hintergrundjobs (ADR-009), Datenbank-Statistiken und
        Systemverwaltung
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="success">FastAPI + SQLModel Backend</Badge>
    </div>
  </div>

  <!-- Primary Horizontal Sub-Navigation Tabs -->
  <div class="relative w-full overflow-hidden">
    <div
      class="no-scrollbar scroll-mask-x flex gap-2 overflow-x-auto rounded-2xl border border-border-subtle bg-surface-50 p-1.5 px-1 py-1.5 select-none"
    >
      {#each navigationTabs as tab}
        <a
          href={tab.path}
          class="flex shrink-0 cursor-pointer items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold whitespace-nowrap no-underline transition-all {activeTab ===
          tab.id
            ? 'bg-surface-0 text-primary shadow-sm'
            : 'text-text-muted hover:text-text-main'}"
        >
          <span>{tab.label}</span>
        </a>
      {/each}
    </div>
  </div>

  {@render children?.()}
</div>
