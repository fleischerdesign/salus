<script lang="ts">
  import { liveQuery } from 'dexie';
  import { mutateDomain } from '$lib/db/mutate-domain';
  import { db } from '$lib/db/database';
  import { pullFull } from '$lib/db/sync-pull';
  import type { AdminUser } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Table from '$components/ui/Table.svelte';
  import Spinner from '$components/ui/Spinner.svelte';

  let users = liveQuery(() => db.admin_user.toArray());

  async function toggleAdmin(user: AdminUser) {
    await mutateDomain({
      url: `/api/v1/admin/users/${user.id}/toggle-admin`,
      method: 'POST'
    });
    await pullFull();
  }

  async function toggleActive(user: AdminUser) {
    await mutateDomain({
      url: `/api/v1/admin/users/${user.id}/toggle-active`,
      method: 'POST'
    });
    await pullFull();
  }

  async function deleteUser(id: number) {
    if (!confirm('Delete this user? This cannot be undone.')) return;
    await mutateDomain({
      url: `/api/v1/admin/users/${id}`,
      method: 'DELETE'
    });
    await pullFull();
  }

  const userColumns = [
    { key: 'username', label: 'User' },
    { key: 'email', label: 'Email' },
    { key: 'is_admin', label: 'Admin' },
    { key: 'is_active', label: 'Active' },
    { key: 'measurement_count', label: 'Entries' },
    { key: 'goal_count', label: 'Goals' },
    { key: 'actions', label: '' }
  ];

  const userRows = $derived(
    ($users ?? []).map((u) => ({
      username: u.username,
      email: u.email ?? '—',
      is_admin: u.is_admin ? 'Yes' : 'No',
      is_active: u.is_active ? 'Active' : 'Inactive',
      measurement_count: String(u.measurement_count ?? 0),
      goal_count: String(u.goal_count ?? 0),
      actions: '',
      _row: u as AdminUser
    }))
  );
</script>

<div class="space-y-6">
  {#if !$users}
    <div class="flex justify-center py-20"><Spinner size="lg" /></div>
  {:else}
    <Card padding={false}>
      {#snippet header()}
        <span class="text-sm font-semibold text-surface-900">Users</span>
      {/snippet}
      {#if ($users ?? []).length > 0}
        <Table columns={userColumns} rows={userRows} {actions} />
      {:else}
        <div class="px-5 py-8 text-center text-sm text-surface-400">No users found.</div>
      {/if}
    </Card>
  {/if}
</div>

{#snippet actions(row: Record<string, unknown>)}
  {@const u = row._row as AdminUser}
  <div class="flex gap-1.5">
    <button
      type="button"
      class="rounded px-2 py-1 text-xs font-medium text-surface-600 transition-colors duration-150 hover:bg-surface-100"
      onclick={() => toggleAdmin(u)}
    >
      {u.is_admin ? 'Demote' : 'Promote'}
    </button>
    <button
      type="button"
      class="rounded px-2 py-1 text-xs font-medium text-surface-600 transition-colors duration-150 hover:bg-surface-100"
      onclick={() => toggleActive(u)}
    >
      {u.is_active ? 'Deactivate' : 'Activate'}
    </button>
    <button
      type="button"
      class="rounded px-2 py-1 text-xs font-medium text-error-600 transition-colors duration-150 hover:bg-error-50"
      onclick={() => deleteUser(u.id)}
    >
      Delete
    </button>
  </div>
{/snippet}
