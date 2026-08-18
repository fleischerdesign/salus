<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import InteractiveChart from '../insights/InteractiveChart.svelte';
  import CorrelationMatrix from '../insights/CorrelationMatrix.svelte';
  import ForecastSimulator from '../insights/ForecastSimulator.svelte';
  import CoachPage from '../pages/CoachPage.svelte';
  import AchievementsPage from '../pages/AchievementsPage.svelte';
  import SettingsPage from '../pages/SettingsPage.svelte';

  export type InsightsTab = 'analytics' | 'coach' | 'achievements' | 'settings';

  let {
    initialTab = 'analytics',
    ontabchange
  } = $props<{
    initialTab?: InsightsTab;
    ontabchange?: (tab: InsightsTab) => void;
  }>();

  let activeTab = $state<InsightsTab>('analytics');

  $effect(() => {
    activeTab = initialTab;
  });

  function setTab(tab: InsightsTab) {
    activeTab = tab;
    ontabchange?.(tab);
  }
</script>

<div class="space-y-6">
  <!-- Workspace Header -->
  <div class="flex items-center justify-between flex-wrap gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Wissenschaftliche Analytik & Intelligenz</h1>
      <p class="text-sm text-[var(--text-muted)] mt-0.5">
        Biometrische Korrelationen, KI-Empfehlungen, Gamification & System-Architektur
      </p>
    </div>
    <div class="flex items-center gap-2">
      <Badge variant="primary">Modell: Pearson r & Forecast Engine</Badge>
    </div>
  </div>

  <!-- Unified Horizontal Sub-Nav Bar (Pill Tabs) -->
  <div class="flex gap-2 bg-[var(--bg-surface-50)] p-1.5 rounded-2xl border border-[var(--border-subtle)] overflow-x-auto">
    <button
      type="button"
      onclick={() => setTab('analytics')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'analytics' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="insights" class="text-[var(--color-primary)]" />
      <span>Analytik & Splines</span>
      <Badge variant="primary" class="text-[0.625rem]">7T-EMA</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('coach')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'coach' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>KI-Health Coach</span>
      <Badge variant="activity" class="text-[0.625rem]">3 Tipps</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('achievements')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'achievements' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="sun" class="text-[var(--color-circadian)]" />
      <span>Achievements & XP</span>
      <Badge variant="default" class="text-[0.625rem]">Lvl 12</Badge>
    </button>

    <button
      type="button"
      onclick={() => setTab('settings')}
      class="px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 cursor-pointer transition-all whitespace-nowrap {activeTab === 'settings' ? 'bg-[var(--bg-surface-0)] text-[var(--color-primary)] shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
    >
      <Icon name="labs" class="text-[var(--text-soft)]" />
      <span>Einstellungen</span>
    </button>
  </div>

  <!-- Workspace Content Area -->
  {#if activeTab === 'analytics'}
    <div class="space-y-4">
      <InteractiveChart data={[]} metricCode="weight" unit="kg" />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <CorrelationMatrix />
        <ForecastSimulator />
      </div>
    </div>
  {:else if activeTab === 'coach'}
    <CoachPage />
  {:else if activeTab === 'achievements'}
    <AchievementsPage />
  {:else if activeTab === 'settings'}
    <SettingsPage />
  {/if}
</div>
