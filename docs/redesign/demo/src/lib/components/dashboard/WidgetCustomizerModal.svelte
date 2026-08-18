<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';

  export interface DashboardWidgetConfig {
    id: string;
    name: string;
    description: string;
    category: 'vital' | 'lifestyle' | 'longevity';
    enabled: boolean;
  }

  let {
    open = false,
    widgets = $bindable<DashboardWidgetConfig[]>([]),
    onclose
  } = $props<{
    open: boolean;
    widgets: DashboardWidgetConfig[];
    onclose: () => void;
  }>();

  function toggleWidget(id: string) {
    const w = widgets.find(item => item.id === id);
    if (w) w.enabled = !w.enabled;
  }

  function resetDefault() {
    widgets.forEach(w => w.enabled = true);
  }
</script>

{#if open}
  <div class="fixed inset-0 bg-black/75 backdrop-blur-md z-60 flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-[var(--glass-dock-bg)] backdrop-blur-2xl border border-[var(--border-subtle)] rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl space-y-6 animate-[fadeIn_0.2s_ease-out]">
      
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold">
            <Icon name="sun" size={22} />
          </div>
          <div>
            <h2 class="text-base font-extrabold text-[var(--text-main)]">Dashboard-Widgets anpassen</h2>
            <p class="text-xs text-[var(--text-muted)]">Wähle die klinischen und biometrischen Widgets für dein Dashboard</p>
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

      <!-- Widget List -->
      <div class="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
        {#each widgets as w}
          <div
            class="p-3.5 rounded-2xl border transition-all flex items-center justify-between gap-3 {w.enabled ? 'bg-[var(--bg-surface-0)] border-[var(--border-subtle)]' : 'bg-[var(--bg-surface-50)]/50 border-[var(--border-subtle)]/50 opacity-60'}"
          >
            <div>
              <div class="flex items-center gap-2">
                <span class="font-extrabold text-xs text-[var(--text-main)]">{w.name}</span>
                <Badge variant={w.category === 'vital' ? 'vital' : w.category === 'longevity' ? 'primary' : 'activity'} class="text-[0.625rem]">
                  {w.category === 'vital' ? 'Klinisch' : w.category === 'longevity' ? 'Langlebigkeit' : 'Lifestyle'}
                </Badge>
              </div>
              <p class="text-[0.6875rem] text-[var(--text-muted)] mt-0.5">{w.description}</p>
            </div>

            <button
              type="button"
              onclick={() => toggleWidget(w.id)}
              class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out {w.enabled ? 'bg-[var(--color-primary)]' : 'bg-[var(--bg-surface-50)] border-[var(--border-subtle)]'}"
              aria-label="Widget umschalten"
            >
              <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {w.enabled ? 'translate-x-5' : 'translate-x-0'}"></span>
            </button>
          </div>
        {/each}
      </div>

      <!-- Bottom Actions -->
      <div class="flex items-center justify-between pt-2 border-t border-[var(--border-subtle)]">
        <button
          type="button"
          onclick={resetDefault}
          class="text-xs text-[var(--text-muted)] hover:text-[var(--text-main)] font-semibold cursor-pointer"
        >
          Auf Standard zurücksetzen
        </button>

        <Btn variant="primary" size="sm" onclick={onclose}>
          Änderungen übernehmen
        </Btn>
      </div>

    </div>
  </div>
{/if}
