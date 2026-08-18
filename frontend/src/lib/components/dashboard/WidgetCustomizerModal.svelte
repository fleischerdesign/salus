<script lang="ts">
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';

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
    const w = widgets.find((item: DashboardWidgetConfig) => item.id === id);
    if (w) w.enabled = !w.enabled;
  }

  function resetDefault() {
    widgets.forEach((w: DashboardWidgetConfig) => (w.enabled = true));
  }
</script>

<Modal
  {open}
  title="Dashboard-Widgets anpassen"
  subtitle="Wähle die klinischen und biometrischen Widgets für dein Dashboard"
  icon="wb-sunny"
  size="md"
  {onclose}
>
  <div class="space-y-4">
    <!-- Widget List -->
    <div class="max-h-[60vh] space-y-2 overflow-y-auto pr-1">
      {#each widgets as w}
        <div
          class="flex items-center justify-between gap-3 rounded-2xl border p-3.5 transition-all {w.enabled
            ? 'border-[var(--border-subtle)] bg-[var(--bg-surface-0)]'
            : 'border-[var(--border-subtle)]/50 bg-[var(--bg-surface-50)]/50 opacity-60'}"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-extrabold text-[var(--text-main)]">{w.name}</span>
              <Badge
                variant={w.category === 'vital'
                  ? 'vital'
                  : w.category === 'longevity'
                    ? 'primary'
                    : 'activity'}
                class="text-[0.625rem]"
              >
                {w.category === 'vital'
                  ? 'Klinisch'
                  : w.category === 'longevity'
                    ? 'Langlebigkeit'
                    : 'Lifestyle'}
              </Badge>
            </div>
            <p class="mt-0.5 text-[0.6875rem] text-[var(--text-muted)]">{w.description}</p>
          </div>

          <button
            type="button"
            onclick={() => toggleWidget(w.id)}
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out {w.enabled
              ? 'bg-[var(--color-primary)]'
              : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)]'}"
            aria-label="Widget umschalten"
          >
            <span
              class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out {w.enabled
                ? 'translate-x-5'
                : 'translate-x-0'}"
            ></span>
          </button>
        </div>
      {/each}
    </div>

    <!-- Bottom Actions -->
    <div class="flex items-center justify-between border-t border-[var(--border-subtle)] pt-2">
      <button
        type="button"
        onclick={resetDefault}
        class="cursor-pointer text-xs font-semibold text-[var(--text-muted)] hover:text-[var(--text-main)]"
      >
        Auf Standard zurücksetzen
      </button>

      <Btn variant="primary" size="md" onclick={onclose}>Änderungen übernehmen</Btn>
    </div>
  </div>
</Modal>
