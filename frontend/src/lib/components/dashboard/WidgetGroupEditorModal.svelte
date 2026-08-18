<script lang="ts">
  import type { DashboardWidget, DashboardWidgetGroup } from '../../types/widget-groups';
  import Btn from '../ui/Btn.svelte';
  import Input from '../ui/Input.svelte';
  import Modal from '../ui/Modal.svelte';

  let {
    open = false,
    group,
    isNew = false,
    onsave,
    ondelete,
    onclose
  } = $props<{
    open: boolean;
    group: DashboardWidgetGroup | null;
    isNew?: boolean;
    onsave: (group: DashboardWidgetGroup) => void;
    ondelete?: (groupId: string) => void;
    onclose: () => void;
  }>();

  let editedTitle = $state('');
  let editedSubtitle = $state('');
  let editedColumns = $state<1 | 2 | 3>(2);
  let editedWidgets = $state<DashboardWidget[]>([]);

  $effect(() => {
    if (open) {
      if (group) {
        editedTitle = group.title;
        editedSubtitle = group.subtitle || '';
        editedColumns = group.columns;
        editedWidgets = [...group.widgets];
      } else {
        editedTitle = '';
        editedSubtitle = '';
        editedColumns = 2;
        editedWidgets = [];
      }
    }
  });

  function moveWidgetUp(index: number) {
    if (index > 0) {
      const temp = editedWidgets[index];
      editedWidgets[index] = editedWidgets[index - 1];
      editedWidgets[index - 1] = temp;
    }
  }

  function moveWidgetDown(index: number) {
    if (index < editedWidgets.length - 1) {
      const temp = editedWidgets[index];
      editedWidgets[index] = editedWidgets[index + 1];
      editedWidgets[index + 1] = temp;
    }
  }

  function removeWidget(index: number) {
    editedWidgets = editedWidgets.filter((_, idx) => idx !== index);
  }

  function handleSave() {
    if (!editedTitle.trim()) return;

    const saved: DashboardWidgetGroup = {
      id: group?.id || `group_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      title: editedTitle.trim(),
      subtitle: editedSubtitle.trim() || undefined,
      columns: editedColumns,
      widgets: editedWidgets
    };

    onsave(saved);
    onclose();
  }
</script>

<Modal
  open={open && Boolean(group || isNew)}
  title={isNew ? 'Neue Widget-Gruppe erstellen' : 'Widget-Gruppe bearbeiten'}
  subtitle="Passe Titel, Raster-Spalten und enthaltene Widgets an"
  icon="dashboard-customize"
  size="md"
  {onclose}
>
  <div class="space-y-4 text-xs">
    <Input
      label="Gruppen-Titel"
      placeholder="z. B. Kardiologie und Vitalzeichen..."
      bind:value={editedTitle}
      required
    />

    <Input
      label="Untertitel (optional)"
      placeholder="z. B. Hämodynamik, Ruhepuls und Sauerstoffsättigung..."
      bind:value={editedSubtitle}
    />

    <div>
      <span class="mb-1 block font-bold text-[var(--text-main)]">Spalten-Layout</span>
      <div class="grid grid-cols-3 gap-2">
        {#each [1, 2, 3] as cols}
          <button
            type="button"
            onclick={() => (editedColumns = cols as 1 | 2 | 3)}
            class="cursor-pointer rounded-xl border px-3 py-2 text-center font-bold transition-all {editedColumns ===
            cols
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-white'
              : 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)] text-[var(--text-muted)]'}"
          >
            {cols === 1 ? '1 Spalte' : cols === 2 ? '2 Spalten' : '3 Spalten'}
          </button>
        {/each}
      </div>
    </div>

    <!-- Widgets in this group -->
    {#if !isNew}
      <div class="pt-2">
        <span class="mb-1.5 block font-bold text-[var(--text-main)]">
          Enthaltene Widgets ({editedWidgets.length})
        </span>
        <div class="max-h-44 space-y-1.5 overflow-y-auto pr-1">
          {#each editedWidgets as w, idx}
            <div
              class="flex items-center justify-between gap-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2.5"
            >
              <span class="truncate text-xs font-semibold text-[var(--text-main)]">{w.title}</span>

              <div class="flex items-center gap-1">
                <button
                  type="button"
                  onclick={() => moveWidgetUp(idx)}
                  disabled={idx === 0}
                  class="h-6 w-6 cursor-pointer rounded bg-[var(--bg-surface-50)] text-[0.625rem] text-[var(--text-muted)] hover:text-[var(--text-main)] disabled:opacity-30"
                >
                  ▲
                </button>
                <button
                  type="button"
                  onclick={() => moveWidgetDown(idx)}
                  disabled={idx === editedWidgets.length - 1}
                  class="h-6 w-6 cursor-pointer rounded bg-[var(--bg-surface-50)] text-[0.625rem] text-[var(--text-muted)] hover:text-[var(--text-main)] disabled:opacity-30"
                >
                  ▼
                </button>
                <button
                  type="button"
                  onclick={() => removeWidget(idx)}
                  class="h-6 w-6 cursor-pointer rounded bg-rose-500/10 text-xs font-bold text-rose-500 transition-all hover:bg-rose-500 hover:text-white"
                  title="Widget entfernen"
                >
                  &times;
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

  <!-- Action Footer -->
  <div class="mt-4 flex items-center justify-between border-t border-[var(--border-subtle)] pt-3">
    {#if !isNew && ondelete && group}
      <button
        type="button"
        onclick={() => {
          if (confirm('Diese Widget-Gruppe wirklich löschen?')) {
            ondelete(group.id);
            onclose();
          }
        }}
        class="cursor-pointer text-xs font-bold text-rose-500 hover:underline"
      >
        Gruppe löschen
      </button>
    {:else}
      <div></div>
    {/if}

    <div class="flex gap-2">
      <Btn variant="secondary" size="md" onclick={onclose}>Abbrechen</Btn>
      <Btn variant="primary" size="md" onclick={handleSave} disabled={!editedTitle.trim()}>
        {isNew ? 'Gruppe anlegen' : 'Speichern'}
      </Btn>
    </div>
  </div>
</Modal>
