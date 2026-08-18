<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';

  let { onopenfood } = $props<{
    onopenfood?: () => void;
  }>();
</script>

<div class="bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-[18px] shadow-[var(--shadow-card)] flex flex-col justify-between">
  <div class="flex items-center justify-between mb-3">
    <div class="text-sm font-bold flex items-center gap-1.5 text-[var(--text-main)]">
      <Icon name="fasting" class="text-[var(--color-fasting)]" />
      <span>Intervallfasten</span>
    </div>
    <Badge variant="fasting">Autophagie</Badge>
  </div>

  <div class="text-center py-3">
    <div class="text-[1.8rem] font-extrabold font-mono tabular-nums text-[var(--text-main)]">
      14:38:22
    </div>
    <div class="text-[0.75rem] font-semibold text-[var(--color-fasting)] uppercase tracking-wider mt-0.5">
      Zone 3: Ketose
    </div>
  </div>

  <div class="text-center text-[0.75rem] text-[var(--text-muted)] mb-3">
    Essensfenster öffnet um <strong class="text-[var(--text-main)]">12:30 Uhr</strong>
  </div>

  <button class="btn btn-secondary w-full" onclick={onopenfood}>
    Mahlzeit erfassen
  </button>
</div>
