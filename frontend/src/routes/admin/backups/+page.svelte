<script lang="ts">
  import { api } from '$lib/api/client';
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import Card from '$components/ui/Card.svelte';
  import Table from '$components/ui/Table.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';

  interface Backup {
    filename: string;
    created_at: string;
    size: string;
  }

  let backups = $state<Backup[]>([]);
  let loading = $state(true);
  let creating = $state(false);
  let error = $state('');
  let success = $state('');
  let passwordConfigured = $state(true);

  let configQuery = liveQuery(() => db.system_config.toArray());

  $effect(() => {
    const config = $configQuery ?? [];
    const pwConfig = config.find((c) => c.key === 'SALUS_BACKUP_PASSWORD');
    passwordConfigured = pwConfig ? pwConfig.is_env_override || pwConfig.db_has_value : false;
  });

  let restoreTarget = $state<string | null>(null);
  let deleteTarget = $state<string | null>(null);

  async function load() {
    error = '';
    loading = true;
    try {
      const backupsRes = await api.GET('/api/v1/admin/backups');
      backups = (backupsRes.data as Backup[]) ?? [];
    } catch {
      error = navigator.onLine
        ? 'Failed to load backups. The server may be unreachable.'
        : 'You are offline. Please check your internet connection.';
    } finally {
      loading = false;
    }
  }

  async function createBackup() {
    creating = true;
    error = '';
    const resp = await mutateDomain({
      url: '/api/v1/admin/backups',
      method: 'POST'
    });
    creating = false;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    success = 'Backup created successfully.';
    await load();
  }

  async function doRestore() {
    if (!restoreTarget) return;
    error = '';
    const resp = await mutateDomain({
      url: `/api/v1/admin/backups/${restoreTarget}/restore`,
      method: 'POST'
    });
    restoreTarget = null;
    if (!resp.ok) {
      error = resp.error ?? 'Request failed';
      return;
    }
    success = 'Database restored successfully. The server may restart.';
    await load();
  }

  async function doDelete() {
    if (!deleteTarget) return;
    await mutateDomain({
      url: `/api/v1/admin/backups/${deleteTarget}`,
      method: 'DELETE'
    });
    deleteTarget = null;
    success = 'Backup deleted.';
    await load();
  }

  async function uploadBackup(e: SubmitEvent) {
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
      const res = await fetch('/api/v1/admin/backups/upload', { method: 'POST', body: fd });
      if (!res.ok) {
        error = 'Upload failed.';
        return;
      }
      success = 'Backup uploaded.';
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
    { key: 'filename', label: 'File' },
    { key: 'created_at', label: 'Date' },
    { key: 'size', label: 'Size' },
    { key: 'actions', label: '' }
  ];
</script>

{#if error}<AlertBanner variant="error" class="mb-4">{error}</AlertBanner>{/if}
{#if success}<AlertBanner variant="success" class="mb-4">{success}</AlertBanner>{/if}
{#if !passwordConfigured}
  <AlertBanner variant="warning" class="mb-4">
    Backup password not configured. Set <code>SALUS_BACKUP_PASSWORD</code> in your environment or database
    to enable encrypted backups.
  </AlertBanner>
{/if}

<ConfirmDialog
  open={restoreTarget !== null}
  title="Restore Backup"
  message="This will overwrite the current database with the selected backup. The server will restart. Continue?"
  onconfirm={doRestore}
  oncancel={() => (restoreTarget = null)}
/>

<ConfirmDialog
  open={deleteTarget !== null}
  title="Delete Backup"
  message="This will permanently delete the backup file."
  onconfirm={doDelete}
  oncancel={() => (deleteTarget = null)}
/>

<div class="space-y-6">
  <Card padding={false}>
    {#snippet header()}
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-surface-900">Backups</span>
        <div class="flex items-center gap-2">
          {#if passwordConfigured}
            <form onsubmit={uploadBackup} class="flex items-center gap-2">
              <input
                type="file"
                accept=".enc"
                class="text-xs text-surface-500 file:mr-2 file:rounded file:border file:border-surface-300 file:bg-surface-50 file:px-2.5 file:py-1 file:text-xs file:font-medium file:text-surface-700"
              />
              <Btn variant="secondary" size="sm" type="submit">
                <Icon name="upload-file" size="sm" />Upload
              </Btn>
            </form>
            <Btn variant="primary" size="sm" loading={creating} onclick={createBackup}>
              <Icon name="add" size="sm" />Create Backup
            </Btn>
          {/if}
        </div>
      </div>
    {/snippet}

    {#if loading}
      <div class="flex justify-center py-12"><Spinner /></div>
    {:else if error && backups.length === 0}
      <div class="px-5 py-10 text-center text-sm text-surface-400">
        Could not load backups. Check your connection and try again.
      </div>
    {:else if backups.length === 0}
      <div class="px-5 py-10 text-center text-sm text-surface-400">
        No backups yet. Create one to get started.
      </div>
    {:else}
      <Table
        {columns}
        rows={backups.map((b) => ({
          filename: b.filename,
          created_at: b.created_at ? new Date(b.created_at).toLocaleString() : '—',
          size: b.size ?? '—',
          actions: '',
          _raw: b
        }))}
        {actions}
      />
    {/if}
  </Card>
</div>

{#snippet actions(row: Record<string, unknown>)}
  {@const b = row._raw as Backup}
  <div class="flex items-center gap-1.5">
    <button
      type="button"
      class="duration-micro rounded px-2 py-1 text-xs font-medium text-surface-600 transition-colors hover:bg-surface-100 hover:text-primary-600"
      onclick={() => (restoreTarget = b.filename)}
    >
      Restore
    </button>
    <button
      type="button"
      class="duration-micro rounded px-2 py-1 text-xs font-medium text-error-600 transition-colors hover:bg-error-50"
      onclick={() => (deleteTarget = b.filename)}
    >
      Delete
    </button>
  </div>
{/snippet}
