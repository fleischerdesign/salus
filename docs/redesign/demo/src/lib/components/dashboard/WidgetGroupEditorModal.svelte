<script lang="ts">
  import type { DashboardWidgetGroup } from '../../types/widget-groups';
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  let {
    open = false,
    group,
    isNew = false,
    onsave,
    ondelete,
    onclose
  } = $props<{
    open: boolean;
    group: DashboardWidgetGroup;
    isNew?: boolean;
    onsave: (group: DashboardWidgetGroup) => void;
    ondelete?: (groupId: string) => void;
    onclose: () => void;
  }>();

  let editedTitle = $state('');
  let editedSubtitle = $state('');
  let editedColumns = $state<1 | 2 | 3>(2);
  let editedWidgets = $state<typeof group.widgets>([]);

  $effect(() => {
    if (group) {
      editedTitle = group.title;
      editedSubtitle = group.subtitle || '';
      editedColumns = group.columns || 2;
      editedWidgets = [...group.widgets];
    }
  });

  function removeWidget(index: number) {
    editedWidgets = editedWidgets.filter((_, i) => i !== index);
  }

  function moveWidgetUp(index: number) {
    if (index <= 0) return;
    const item = editedWidgets[index];
    const newArr = [...editedWidgets];
    newArr.splice(index, 1);
    newArr.splice(index - 1, 0, item);
    editedWidgets = newArr;
  }

  function moveWidgetDown(index: number) {
    if (index >= editedWidgets.length - 1) return;
    const item = editedWidgets[index];
    const newArr = [...editedWidgets];
    newArr.splice(index, 1);
    newArr.splice(index + 1, 0, item);
    editedWidgets = newArr;
  }

  function handleSave() {
    if (!editedTitle.trim()) return;
    const updated: DashboardWidgetGroup = {
      ...group,
      title: editedTitle.trim(),
      subtitle: editedSubtitle.trim(),
      columns: editedColumns,
      widgets: editedWidgets
    };
    onsave(updated);
    onclose();
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl space-y-5 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold">
            <Icon name="sun" size={22} />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">
              {isNew ? 'Neue Widget-Gruppe erstellen' : 'Widget-Gruppe bearbeiten'}
            </h2>
            <p class="text-xs text-[var(--text-muted)]">Passe Titel, Raster-Spalten und enthaltene Widgets an</p>
          </div>
        </div>
        <button
          type="button"
          onclick={onclose}
          class="text-[var(--text-muted)] hover:text-[var(--text-main)] text-xl cursor-pointer"
        >
          &times;
        </button>
      </div>

      <!-- Form Fields -->
      <div class="space-y-3.5 text-xs">
        <div>
          <label for="group-title-input" class="block font-bold text-[var(--text-main)] mb-1">Gruppen-Titel</label>
          <input
            id="group-title-input"
            type="text"
            placeholder="z. B. Kardiologie und Vitalzeichen..."
            bind:value={editedTitle}
            class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] text-xs"
          />
        </div>

        <div>
          <label for="group-subtitle-input" class="block font-bold text-[var(--text-main)] mb-1">Untertitel (optional)</label>
          <input
            id="group-subtitle-input"
            type="text"
            placeholder="z. B. Hämodynamik, Ruhepuls und Sauerstoffsättigung..."
            bind:value={editedSubtitle}
            class="w-full px-3.5 py-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-main)] outline-none focus:border-[var(--color-primary)] text-xs"
          />
        </div>

        <div>
          <span class="block font-bold text-[var(--text-main)] mb-1">Spalten-Layout</span>
          <div class="grid grid-cols-3 gap-2">
            {#each [1, 2, 3] as cols}
              <button
                type="button"
                onclick={() => editedColumns = cols as 1 | 2 | 3}
                class="py-2 px-3 rounded-xl border text-center font-bold cursor-pointer transition-all {editedColumns === cols ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]' : 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)] text-[var(--text-muted)]'}"
              >
                {cols === 1 ? '1 Spalte' : cols === 2 ? '2 Spalten' : '3 Spalten'}
              </button>
            {/each}
          </div>
        </div>

        <!-- Widgets in this group -->
        {#if !isNew}
          <div class="pt-2">
            <span class="block font-bold text-[var(--text-main)] mb-1.5">
              Enthaltene Widgets ({editedWidgets.length})
            </span>
            <div class="space-y-1.5 max-h-44 overflow-y-auto pr-1">
              {#each editedWidgets as w, idx}
                <div class="p-2.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] flex items-center justify-between gap-2">
                  <span class="font-semibold text-[var(--text-main)] text-xs truncate">{w.title}</span>
                  
                  <div class="flex items-center gap-1">
                    <button
                      type="button"
                      onclick={() => moveWidgetUp(idx)}
                      disabled={idx === 0}
                      class="w-6 h-6 rounded bg-[var(--bg-surface-50)] text-[var(--text-muted)] disabled:opacity-30 hover:text-[var(--text-main)] text-[0.625rem]"
                    >
                      ▲
                    </button>
                    <button
                      type="button"
                      onclick={() => moveWidgetDown(idx)}
                      disabled={idx === editedWidgets.length - 1}
                      class="w-6 h-6 rounded bg-[var(--bg-surface-50)] text-[var(--text-muted)] disabled:opacity-30 hover:text-[var(--text-main)] text-[0.625rem]"
                    >
                      ▼
                    </button>
                    <button
                      type="button"
                      onclick={() => removeWidget(idx)}
                      class="w-6 h-6 rounded bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all text-xs font-bold"
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
      <div class="flex items-center justify-between pt-3 border-t border-[var(--border-subtle)]">
        {#if !isNew && ondelete}
          <button
            type="button"
            onclick={() => {
              if (confirm('Diese Widget-Gruppe wirklich löschen?')) {
                ondelete(group.id);
                onclose();
              }
            }}
            class="text-xs text-rose-500 hover:underline font-bold cursor-pointer"
          >
            Gruppe löschen
          </button>
        {:else}
          <div></div>
        {/if}

        <div class="flex gap-2">
          <Btn variant="secondary" size="sm" onclick={onclose}>
            Abbrechen
          </Btn>
          <Btn variant="primary" size="sm" onclick={handleSave}>
            {isNew ? 'Gruppe anlegen' : 'Speichern'}
          </Btn>
        </div>
      </div>

    </div>
  </div>
{/if}
