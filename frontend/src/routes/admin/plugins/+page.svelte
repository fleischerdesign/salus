<script lang="ts">
  import { api } from '$lib/api/client';
  import { getAuthHeaders } from '$lib/api/headers';
  import Card from '$components/ui/Card.svelte';
  import Table from '$components/ui/Table.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';

  interface Plugin {
    plugin_id: string;
    name: string;
    version: string;
    enabled: boolean;
    loaded: boolean;
    description?: string;
  }

  let plugins = $state<Plugin[]>([]);
  let loading = $state(true);
  let error = $state('');
  let success = $state('');

  async function load() {
    error = '';
    loading = true;
    try {
      const { data } = await api.GET('/api/v1/admin/plugins');
      plugins = (data as Plugin[]) ?? [];
    } catch {
      error = navigator.onLine
        ? 'Failed to load plugins. The server may be unreachable.'
        : 'You are offline. Please check your internet connection.';
    } finally {
      loading = false;
    }
  }

  async function togglePlugin(plugin: Plugin) {
    const res = await fetch(`/api/v1/admin/plugins/${plugin.plugin_id}/toggle`, {
      method: 'POST',
      headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable: !plugin.enabled })
    });
    if (!res.ok) {
      try {
        const body = await res.json();
        error = body.detail ?? body.message ?? 'Request failed';
      } catch {
        error = 'Request failed';
      }
      return;
    }
    await load();
  }

  async function uninstallPlugin(plugin: Plugin) {
    if (!confirm(`Uninstall ${plugin.name}?`)) return;
    await fetch(`/api/v1/admin/plugins/${plugin.plugin_id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    await load();
  }

  async function uploadPlugin(e: SubmitEvent) {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const fileInput = form.querySelector('input[type="file"]') as HTMLInputElement;
    if (!fileInput?.files?.[0]) {
      error = 'Select a file.';
      return;
    }
    const fd = new FormData();
    fd.append('file', fileInput.files[0]);
    try {
      const res = await fetch('/api/v1/admin/plugins/upload', { method: 'POST', body: fd });
      if (!res.ok) {
        error = 'Upload failed.';
        return;
      }
      success = 'Plugin uploaded.';
      fileInput.value = '';
      await load();
    } catch {
      error = navigator.onLine
        ? 'Upload failed. The server may be unreachable.'
        : 'You are offline. Please check your internet connection.';
    }
  }

  load();

  const columns = [
    { key: 'name', label: 'Plugin' },
    { key: 'version', label: 'Version' },
    { key: 'actions', label: '' }
  ];
</script>

{#if error}<AlertBanner variant="error" class="mb-4">{error}</AlertBanner>{/if}
{#if success}<AlertBanner variant="success" class="mb-4">{success}</AlertBanner>{/if}

<div class="space-y-6">
  <Card padding={false}>
    {#snippet header()}
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-surface-900">Developer Plugins</span>
        <form onsubmit={uploadPlugin} class="flex items-center gap-2">
          <input
            type="file"
            accept=".zip"
            class="text-xs text-surface-500 file:mr-2 file:rounded file:border file:border-surface-300 file:bg-surface-50 file:px-2.5 file:py-1 file:text-xs file:font-medium file:text-surface-700"
          />
          <Btn variant="secondary" size="sm" type="submit">
            <Icon name="upload-file" size="sm" />Install
          </Btn>
        </form>
      </div>
    {/snippet}

    {#if loading}
      <div class="flex justify-center py-12"><Spinner /></div>
    {:else if error && plugins.length === 0}
      <div class="px-5 py-10 text-center text-sm text-surface-400">
        Could not load plugins. Check your connection and try again.
      </div>
    {:else if plugins.length === 0}
      <div class="px-5 py-10 text-center text-sm text-surface-400">
        No plugins installed. Upload a .zip to get started.
      </div>
    {:else}
      <Table
        {columns}
        rows={plugins.map((p) => ({
          name: `${p.name}\n${p.description ?? ''}`,
          version: p.version ?? '—',
          actions: '',
          _raw: p
        }))}
        {actions}
      />
    {/if}
  </Card>
</div>

{#snippet actions(row: Record<string, unknown>)}
  {@const p = row._raw as Plugin}
  <div class="flex items-center gap-1.5">
    <Badge variant={p.enabled ? 'success' : 'default'}>
      {p.enabled ? 'Enabled' : 'Disabled'}
    </Badge>
    <button
      type="button"
      class="duration-micro rounded px-2 py-1 text-xs font-medium text-surface-600 transition-colors hover:bg-surface-100"
      onclick={() => togglePlugin(p)}
    >
      {p.enabled ? 'Disable' : 'Enable'}
    </button>
    <button
      type="button"
      class="duration-micro rounded px-2 py-1 text-xs font-medium text-error-600 transition-colors hover:bg-error-50"
      onclick={() => uninstallPlugin(p)}
    >
      Remove
    </button>
  </div>
{/snippet}
