<script lang="ts">
  import WorkoutsPage from '../pages/WorkoutsPage.svelte';
  import NutritionPage from '../pages/NutritionPage.svelte';
  import FastingPage from '../pages/FastingPage.svelte';
  import HabitsPage from '../pages/HabitsPage.svelte';
  import JournalPage from '../pages/JournalPage.svelte';

  export type TrackTab = 'workouts' | 'food' | 'fasting' | 'habits' | 'journal';

  let {
    activeTab = 'workouts',
    onopenbarcode
  } = $props<{
    activeTab?: TrackTab;
    onopenbarcode?: () => void;
  }>();
</script>

<div class="space-y-6">
  <!-- Workspace Content Area (Driven by Topbar Ribbon) -->
  {#if activeTab === 'workouts'}
    <WorkoutsPage />
  {:else if activeTab === 'food'}
    <NutritionPage {onopenbarcode} />
  {:else if activeTab === 'fasting'}
    <FastingPage />
  {:else if activeTab === 'habits'}
    <HabitsPage />
  {:else if activeTab === 'journal'}
    <JournalPage />
  {/if}
</div>
