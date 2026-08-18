<script lang="ts">
  // Navigation & Core Primitives
  import FloatingGlassDock from './lib/components/nav/FloatingGlassDock.svelte';
  import Btn from './lib/components/ui/Btn.svelte';
  import type { PageId } from './lib/types';
  import type { DashboardItem, DashboardWidgetGroup, DashboardWidget } from './lib/types/widget-groups';

  // Dedicated Pages
  import MetricsOverviewPage from './lib/components/pages/MetricsOverviewPage.svelte';
  import MetricGroupDetailPage from './lib/components/pages/MetricGroupDetailPage.svelte';
  import MetricSingleDetailPage from './lib/components/pages/MetricSingleDetailPage.svelte';
  import WorkoutsPage, { type WorkoutTab } from './lib/components/pages/WorkoutsPage.svelte';
  import NutritionPage, { type NutritionTab } from './lib/components/pages/NutritionPage.svelte';
  import FastingPage from './lib/components/pages/FastingPage.svelte';
  import GoalsPage from './lib/components/pages/GoalsPage.svelte';
  import CoachPage from './lib/components/pages/CoachPage.svelte';
  import AchievementsPage from './lib/components/pages/AchievementsPage.svelte';
  import LabsPage from './lib/components/pages/LabsPage.svelte';
  import CommunityPage, { type CommunityTab } from './lib/components/pages/CommunityPage.svelte';
  import OpenSciencePage from './lib/components/pages/OpenSciencePage.svelte';
  import MedicationsPage from './lib/components/pages/MedicationsPage.svelte';
  import HabitsPage from './lib/components/pages/HabitsPage.svelte';
  import JournalPage from './lib/components/pages/JournalPage.svelte';
  import SettingsPage from './lib/components/pages/SettingsPage.svelte';
  import AdminPage from './lib/components/admin/AdminPage.svelte';

  // Dashboard Dynamic Items Architecture & Gallery
  import DashboardDateBar from './lib/components/dashboard/DashboardDateBar.svelte';
  import DynamicWidgetGroup from './lib/components/dashboard/DynamicWidgetGroup.svelte';
  import WidgetRenderer from './lib/components/dashboard/WidgetRenderer.svelte';
  import WidgetGalleryModal from './lib/components/dashboard/WidgetGalleryModal.svelte';
  import WidgetGroupEditorModal from './lib/components/dashboard/WidgetGroupEditorModal.svelte';

  // Analytics & Insights Components
  import InteractiveChart from './lib/components/insights/InteractiveChart.svelte';
  import CorrelationMatrix from './lib/components/insights/CorrelationMatrix.svelte';
  import ForecastSimulator from './lib/components/insights/ForecastSimulator.svelte';
  import AchievementCard from './lib/components/gamification/AchievementCard.svelte';

  // Modals & Drawers
  import QuickLogModal from './lib/components/modals/QuickLogModal.svelte';
  import CommandPalette from './lib/components/modals/CommandPalette.svelte';
  import ConflictResolverModal from './lib/components/modals/ConflictResolverModal.svelte';
  import BarcodeScannerModal from './lib/components/food/BarcodeScannerModal.svelte';
  import ClinicalPdfReportModal from './lib/components/labs/ClinicalPdfReportModal.svelte';
  import NotificationDrawer from './lib/components/layout/NotificationDrawer.svelte';
  import OnboardingModal from './lib/components/onboarding/OnboardingModal.svelte';

  let currentPage = $state<PageId>('dashboard');
  let selectedGroupKey = $state<string>('blood_pressure');
  let selectedMetricCode = $state<string>('systolic_bp');

  let isQuickLogOpen = $state(false);
  let isCmdKOpen = $state(false);
  let isConflictModalOpen = $state(false);
  let isBarcodeModalOpen = $state(false);
  let isPdfModalOpen = $state(false);
  let isNotificationDrawerOpen = $state(false);
  let isOnboardingOpen = $state(false);

  // Widget Group Engine & iOS Edit Mode States
  let isEditMode = $state(false);
  let isGalleryOpen = $state(false);
  let isGroupEditorOpen = $state(false);
  let isCreatingNewGroup = $state(false);
  let activeGroupForGallery = $state<DashboardWidgetGroup | null>(null);
  let activeGroupForEdit = $state<DashboardWidgetGroup | null>(null);

  let selectedDashboardDate = $state('2026-08-17');
  let waterAmount = $state(2250);

  // Unified Dashboard Structure: Supports BOTH Standalone Widgets AND Visual Group Sections!
  let dashboardItems = $state<DashboardItem[]>([
    // 1. Standalone Loose Widget: Circadian Sun Arc
    {
      id: 'item_circadian',
      kind: 'widget',
      widget: { id: 'w_circadian_1', type: 'circadian_arc', title: 'Zirkadianer 24h-Sonnenbogen', size: 'full' }
    },
    // 2. Group: Kardiologie
    {
      id: 'item_grp_cardio',
      kind: 'group',
      group: {
        id: 'grp_cardio',
        title: 'Kardiologie und Hämodynamik',
        subtitle: 'Arterieller Blutdruck nach ESC 2024, Ruhepuls-Trend und Sauerstoffsättigung',
        columns: 2,
        widgets: [
          { id: 'w_bp_1', type: 'blood_pressure_dial', title: 'Arterieller Blutdruck', size: 'half' },
          { id: 'w_rhr_1', type: 'rhr_sparkline', title: 'Ruhepuls (7T-Trend)', size: 'half' },
          { id: 'w_spo2_1', type: 'spo2_vo2max', title: 'SpO2 und VO2 Max', size: 'half' }
        ]
      }
    },
    // 3. Group: Glukosestoffwechsel
    {
      id: 'item_grp_metabolism',
      kind: 'group',
      group: {
        id: 'grp_metabolism',
        title: 'Glukosestoffwechsel und Fastenuhr',
        subtitle: 'Kontinuierliche Glukosekurve, Time in Range und Autophagie-Phasen',
        columns: 2,
        widgets: [
          { id: 'w_cgm_1', type: 'cgm_wave', title: 'Kontinuierliche Glukosekurve (CGM)', size: 'half' },
          { id: 'w_fasting_1', type: 'fasting_clock', title: '16:8 Fasten-Stoffwechseluhr', size: 'half' },
          { id: 'w_tir_1', type: 'time_in_range', title: 'Time in Range (TIR)', size: 'half' }
        ]
      }
    },
    // 4. Group: Regeneration & Schlaf
    {
      id: 'item_grp_recovery',
      kind: 'group',
      group: {
        id: 'grp_recovery',
        title: 'Regeneration, Schlaf und Neurologie',
        subtitle: 'ZNS-Erholungsbatterie, Hypnogramm und autonome Balance',
        columns: 2,
        widgets: [
          { id: 'w_rec_1', type: 'recovery_battery', title: 'ZNS-Erholungsbatterie', size: 'half' },
          { id: 'w_sleep_1', type: 'sleep_hypnogram', title: 'Schlafarchitektur und Schlafschuld', size: 'half' },
          { id: 'w_ans_1', type: 'ans_balance', title: 'Autonome Nervensystem-Balance', size: 'half' },
          { id: 'w_meds_1', type: 'medication_dose', title: 'Medikamenten- und Einnahmeplan', size: 'half' }
        ]
      }
    },
    // 5. Group: Körperzusammensetzung & Energie
    {
      id: 'item_grp_body_energy',
      kind: 'group',
      group: {
        id: 'grp_body_energy',
        title: 'Körperzusammensetzung und Energieumsatz',
        subtitle: 'BIA-Zusammensetzung, Hydration und stündliches Aktivitäts-Histogramm',
        columns: 2,
        widgets: [
          { id: 'w_bia_1', type: 'bia_spectrum', title: 'BIA-Zusammensetzungsspektrum', size: 'half' },
          { id: 'w_hydro_1', type: 'hydration_glass', title: 'Hydration Wave Glass', size: 'half' },
          { id: 'w_act_1', type: 'activity_histogram', title: 'Diurnales Schritt-Histogramm', size: 'half' },
          { id: 'w_rings_1', type: 'hero_rings', title: 'Biometrische Progress-Ringe', size: 'half' }
        ]
      }
    },
    // 6. Standalone Loose Widgets: Habits
    {
      id: 'item_habits_pills',
      kind: 'widget',
      widget: { id: 'w_hab_pills', type: 'habits_pills', title: 'Tages-Gewohnheiten Checkliste', size: 'full' }
    },
    {
      id: 'item_habits_year',
      kind: 'widget',
      widget: { id: 'w_hab_year', type: 'habits_year', title: '52-Wochen Konsistenz-Matrix', size: 'full' }
    }
  ]);

  // Open Gallery for a specific Group
  function openGalleryForGroup(group: DashboardWidgetGroup) {
    activeGroupForGallery = group;
    isGalleryOpen = true;
  }

  // Open Gallery for Dashboard Root (adds loose widget or creates group)
  function openRootGallery() {
    activeGroupForGallery = null;
    isGalleryOpen = true;
  }

  function handleAddWidget(widget: DashboardWidget, targetGroupId: string | null) {
    if (targetGroupId) {
      // Add into specific group
      for (const item of dashboardItems) {
        if (item.kind === 'group' && item.group.id === targetGroupId) {
          item.group.widgets = [...item.group.widgets, widget];
          dashboardItems = [...dashboardItems];
          return;
        }
      }
    } else {
      // Add as loose standalone widget on root
      const newItem: DashboardItem = {
        id: `item_${Date.now()}`,
        kind: 'widget',
        widget
      };
      dashboardItems = [...dashboardItems, newItem];
    }
  }

  function handleRemoveRootItem(itemId: string) {
    dashboardItems = dashboardItems.filter(item => item.id !== itemId);
  }

  function handleRemoveGroupWidget(groupId: string, widgetId: string) {
    for (const item of dashboardItems) {
      if (item.kind === 'group' && item.group.id === groupId) {
        item.group.widgets = item.group.widgets.filter(w => w.id !== widgetId);
        dashboardItems = [...dashboardItems];
        return;
      }
    }
  }

  function openEditGroup(group: DashboardWidgetGroup) {
    activeGroupForEdit = group;
    isCreatingNewGroup = false;
    isGroupEditorOpen = true;
  }

  function openCreateGroup() {
    activeGroupForEdit = {
      id: `grp_${Date.now()}`,
      title: 'Neue Gruppe',
      subtitle: '',
      columns: 2,
      widgets: []
    };
    isCreatingNewGroup = true;
    isGroupEditorOpen = true;
  }

  function handleSaveGroup(savedGroup: DashboardWidgetGroup) {
    if (isCreatingNewGroup) {
      const newItem: DashboardItem = {
        id: `item_${savedGroup.id}`,
        kind: 'group',
        group: savedGroup
      };
      dashboardItems = [...dashboardItems, newItem];
    } else {
      const idx = dashboardItems.findIndex(item => item.kind === 'group' && item.group.id === savedGroup.id);
      if (idx !== -1) {
        dashboardItems[idx] = {
          id: dashboardItems[idx].id,
          kind: 'group',
          group: savedGroup
        };
        dashboardItems = [...dashboardItems];
      }
    }
  }

  function handleDeleteGroup(groupId: string) {
    dashboardItems = dashboardItems.filter(item => !(item.kind === 'group' && item.group.id === groupId));
  }

  function moveItemUp(index: number) {
    if (index <= 0) return;
    const item = dashboardItems[index];
    const newArr = [...dashboardItems];
    newArr.splice(index, 1);
    newArr.splice(index - 1, 0, item);
    dashboardItems = newArr;
  }

  function moveItemDown(index: number) {
    if (index >= dashboardItems.length - 1) return;
    const item = dashboardItems[index];
    const newArr = [...dashboardItems];
    newArr.splice(index, 1);
    newArr.splice(index + 1, 0, item);
    dashboardItems = newArr;
  }

  function handleWaterSubmit(amount: number) {
    waterAmount = Math.min(3000, waterAmount + amount);
  }

  function toggleTheme() {
    document.documentElement.classList.toggle('dark');
  }

  function navigateTo(page: PageId, groupKey?: string, metricCode?: string) {
    if (groupKey) selectedGroupKey = groupKey;
    if (metricCode) selectedMetricCode = metricCode;
    currentPage = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  let workoutTab = $derived<WorkoutTab>(
    currentPage === 'workouts-plans' ? 'plans' :
    currentPage === 'workouts-sessions' ? 'sessions' :
    currentPage === 'workouts-exercises' ? 'exercises' :
    'active'
  );

  let nutritionTab = $derived<NutritionTab>(
    currentPage === 'food-recipes' ? 'recipes' :
    currentPage === 'food-database' ? 'database' :
    'diary'
  );

  let communityTab = $derived<CommunityTab>(
    currentPage === 'community-connections' ? 'connections' :
    currentPage === 'community-feed' ? 'feed' :
    currentPage === 'community-audit' ? 'audit' :
    currentPage === 'open-science' ? 'open_science' :
    'leaderboard'
  );

  // Global Keyboard Shortcuts
  function handleKeyDown(e: KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      isCmdKOpen = !isCmdKOpen;
    } else if (e.key === 'l' || e.key === 'L') {
      if (!isQuickLogOpen && !isCmdKOpen && (e.target as HTMLElement).tagName !== 'INPUT') {
        e.preventDefault();
        isQuickLogOpen = true;
      }
    } else if (e.key === 'Escape') {
      if (isEditMode) {
        isEditMode = false;
      }
      isQuickLogOpen = false;
      isCmdKOpen = false;
      isConflictModalOpen = false;
      isBarcodeModalOpen = false;
      isPdfModalOpen = false;
      isNotificationDrawerOpen = false;
      isOnboardingOpen = false;
      isGalleryOpen = false;
      isGroupEditorOpen = false;
    }
  }
</script>

<svelte:window onkeydown={handleKeyDown} />

<div class="min-h-screen bg-[var(--bg-canvas)] text-[var(--text-main)] flex flex-col font-sans transition-colors duration-200">
  <!-- FLOATING CONTEXTUAL GLASS DOCK WITH FLYOUT DECKS -->
  <FloatingGlassDock
    activeView={currentPage}
    onnavigate={navigateTo}
    onopenquicklog={() => isQuickLogOpen = true}
    onopencmdk={() => isCmdKOpen = true}
    ontoggletheme={toggleTheme}
    onopennotifications={() => isNotificationDrawerOpen = true}
    onopenonboarding={() => isOnboardingOpen = true}
  />

  <!-- MAIN CANVAS CONTAINER -->
  <main class="w-full max-w-[1200px] mx-auto px-5 py-6 pb-28 md:px-6 md:py-8 md:pb-12 flex-1">
    
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 1. DASHBOARD (BENUTZERDEFINIERTE WIDGETS & GRUPPEN)         -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'dashboard'}
      <div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 flex-wrap">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight">Dashboard</h1>
          <p class="text-xs sm:text-sm text-[var(--text-muted)] mt-0.5">Individuell konfigurierbare Biometrie-Zentrale für Philipp</p>
        </div>

        <!-- Interactive Date Navigator -->
        <DashboardDateBar
          bind:selectedDate={selectedDashboardDate}
          todayDate="2026-08-17"
        />

        <!-- Header Action Controls -->
        <div class="flex gap-2 flex-wrap items-center">
          {#if isEditMode}
            <!-- iOS Style Edit Mode Action: [+] Hinzufügen (öffnet Galerie für lose Widgets & Gruppen) + [Fertig] -->
            <button
              type="button"
              onclick={openRootGallery}
              class="px-3.5 py-1.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-bold hover:opacity-90 transition-all cursor-pointer flex items-center gap-1.5 shadow-sm animate-[fadeIn_0.15s_ease-out]"
            >
              <span class="text-sm font-extrabold">+</span>
              <span>Hinzufügen</span>
            </button>

            <button
              type="button"
              onclick={() => isEditMode = false}
              class="px-3.5 py-1.5 rounded-xl bg-emerald-500 text-white text-xs font-bold hover:bg-emerald-600 transition-all cursor-pointer flex items-center gap-1 shadow-sm"
            >
              <span>Fertig</span>
            </button>
          {:else}
            <!-- Standard Clean Mode Button: [Anpassen] -->
            <button
              type="button"
              onclick={() => isEditMode = true}
              class="px-3.5 py-1.5 rounded-xl bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] text-[var(--text-main)] hover:bg-[var(--bg-surface-50)] text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
            >
              <span>Anpassen</span>
            </button>

            <Btn variant="secondary" size="sm" onclick={() => isOnboardingOpen = true}>
              Einführung
            </Btn>
            <Btn variant="secondary" size="sm" onclick={() => navigateTo('metrics-overview')}>
              Metriken &rarr;
            </Btn>
          {/if}
        </div>
      </div>

      <!-- DYNAMIC USER DASHBOARD (Loose Standalone Widgets + Visual Groups) -->
      <div class="space-y-5">
        {#each dashboardItems as item, idx (item.id)}
          <!-- CASE A: Standalone Loose Widget on Dashboard Canvas -->
          {#if item.kind === 'widget'}
            <div
              class="relative transition-transform mb-5 {isEditMode ? (idx % 2 === 0 ? 'ios-wiggle-even' : 'ios-wiggle-odd') : ''}"
            >
              {#if isEditMode}
                <button
                  type="button"
                  onclick={() => handleRemoveRootItem(item.id)}
                  class="absolute -top-2 -right-2 z-30 w-6 h-6 rounded-full bg-rose-500 text-white font-extrabold text-sm flex items-center justify-center shadow-lg hover:scale-110 active:scale-95 transition-transform cursor-pointer border-2 border-[var(--bg-canvas)] animate-[scaleIn_0.15s_ease-out]"
                  title="Widget entfernen"
                  aria-label="Widget entfernen"
                >
                  &times;
                </button>
              {/if}

              <WidgetRenderer
                widget={item.widget}
                {waterAmount}
                onopenfasting={() => navigateTo('fasting')}
              />
            </div>

          <!-- CASE B: Visual Group Container -->
          {:else if item.kind === 'group'}
            <DynamicWidgetGroup
              group={item.group}
              {isEditMode}
              {waterAmount}
              onopenfasting={() => navigateTo('fasting')}
              oneditgroup={openEditGroup}
              onaddwidget={openGalleryForGroup}
              onremovewidget={handleRemoveGroupWidget}
              onmoveup={() => moveItemUp(idx)}
              onmovedown={() => moveItemDown(idx)}
              ondeletegroup={() => handleDeleteGroup(item.group.id)}
            />
          {/if}
        {/each}

        <!-- Bottom Add Dropzone Card (in Edit Mode) -->
        {#if isEditMode}
          <button
            type="button"
            onclick={openRootGallery}
            class="w-full min-h-[90px] rounded-3xl border-2 border-dashed border-[var(--border-subtle)] hover:border-[var(--color-primary)] bg-[var(--bg-surface-0)]/20 hover:bg-[var(--color-primary)]/5 text-[var(--text-muted)] hover:text-[var(--color-primary)] flex items-center justify-center gap-3 p-4 transition-all cursor-pointer group shadow-xs"
          >
            <div class="w-8 h-8 rounded-xl bg-[var(--bg-surface-50)] group-hover:bg-[var(--color-primary)] group-hover:text-white border border-[var(--border-subtle)] flex items-center justify-center font-bold text-base transition-all">
              +
            </div>
            <span class="text-xs font-bold text-[var(--text-main)] group-hover:text-[var(--color-primary)]">
              Weiteres Widget oder neue Gruppe zum Dashboard hinzufügen
            </span>
          </button>
        {/if}
      </div>

      {#if dashboardItems.length === 0}
        <div class="p-12 text-center border-2 border-dashed border-[var(--border-subtle)] rounded-3xl space-y-3">
          <p class="text-sm text-[var(--text-muted)]">Dein Dashboard ist leer.</p>
          <Btn variant="primary" onclick={openRootGallery}>
            + Erstes Element hinzufügen
          </Btn>
        </div>
      {/if}
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 2. METRIKEN: ALLE GRUPPEN & KATALOG                        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'metrics-overview'}
      <MetricsOverviewPage
        onSelectGroup={(gk) => navigateTo('metric-group-detail', gk)}
        onSelectMetric={(gk, mc) => navigateTo('metric-single-detail', gk, mc)}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 3. METRIKEN: GRUPPEN-DETAIL (Z.B. BLUTDRUCK)               -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'metric-group-detail'}
      <MetricGroupDetailPage
        groupKey={selectedGroupKey}
        onBack={() => navigateTo('metrics-overview')}
        onSelectMetric={(gk, mc) => navigateTo('metric-single-detail', gk, mc)}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 4. METRIKEN: EINZEL-DETAIL (Z.B. SYSTOLISCH)               -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'metric-single-detail'}
      <MetricSingleDetailPage
        groupKey={selectedGroupKey}
        metricCode={selectedMetricCode}
        onBackGroup={() => navigateTo('metric-group-detail', selectedGroupKey)}
        onBackAll={() => navigateTo('metrics-overview')}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 5. WORKOUTS (TRAINING & KRAFTSPORT SUITE)                  -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage.startsWith('workouts') || currentPage === 'track'}
      <WorkoutsPage
        initialTab={workoutTab}
        ontabchange={(tab) => {
          if (tab === 'active') currentPage = 'workouts-active';
          else if (tab === 'plans') currentPage = 'workouts-plans';
          else if (tab === 'sessions') currentPage = 'workouts-sessions';
          else if (tab === 'exercises') currentPage = 'workouts-exercises';
        }}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 6. ERNÄHRUNG & MAKROS (VOLLWERTIGE NUTRITION SUITE)        -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage.startsWith('food')}
      <NutritionPage
        initialTab={nutritionTab}
        onopenbarcode={() => isBarcodeModalOpen = true}
        ontabchange={(tab) => {
          if (tab === 'diary') currentPage = 'food-diary';
          else if (tab === 'recipes') currentPage = 'food-recipes';
          else if (tab === 'database') currentPage = 'food-database';
        }}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 7. FASTEN & AUTOPHAGIE-SUITE                               -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'fasting'}
      <FastingPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 8. ZIELE & STATISTISCHE FORECASTS                          -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'goals'}
      <GoalsPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 9. KI-HEALTH COACH & EVIDENZ-INSIGHTS                      -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'coach'}
      <CoachPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 10. AKADEMISCHE ACHIEVEMENTS & XP-RÄNGE                    -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'achievements'}
      <AchievementsPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 11. LABS (KLINISCHE PARAMETER & ARZT-FREIGABE)             -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'labs' || currentPage === 'klinik'}
      <LabsPage onopenpdf={() => isPdfModalOpen = true} />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 12. MEDIKAMENTE & SUPPLEMENTE                              -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'medications'}
      <MedicationsPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 13. GEWOHNHEITEN & HABITS                                  -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'habits'}
      <HabitsPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 14. JOURNAL & REFLEXION                                    -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'journal'}
      <JournalPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 15. COMMUNITY & RANGLISTEN (VOLLWERTIG MIT SUB-ROUTING)    -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage.startsWith('community')}
      <CommunityPage
        initialTab={communityTab}
        ontabchange={(tab) => {
          if (tab === 'leaderboard') currentPage = 'community-leaderboard';
          else if (tab === 'connections') currentPage = 'community-connections';
          else if (tab === 'feed') currentPage = 'community-feed';
          else if (tab === 'audit') currentPage = 'community-audit';
          else if (tab === 'open_science') currentPage = 'open-science';
        }}
      />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 16. OPEN SCIENCE & FORSCHUNG                               -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'open-science'}
      <OpenSciencePage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 17. INSIGHTS (ANALYTIK & KORRELATIONEN)                    -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'insights'}
      <div class="mb-5">
        <h1 class="text-2xl font-extrabold tracking-tight">Wissenschaftliche Analytik und Prognosen</h1>
        <p class="text-sm text-[var(--text-muted)] mt-0.5">Berechnet nach Pearson r mit Signifikanz-Prüfung (p &lt; 0.05)</p>
      </div>

      <!-- Interaktiver Trend-Spline mit 7T-EMA -->
      <div class="mb-4">
        <InteractiveChart data={[]} metricCode="weight" unit="kg" />
      </div>

      <!-- Korrelations-Matrix & Was-wäre-wenn Prognose-Simulator -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <CorrelationMatrix />
        <ForecastSimulator />
      </div>

      <!-- Akademische Achievements -->
      <AchievementCard />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 18. SYSTEM-EINSTELLUNGEN & PROFIL                          -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'settings'}
      <SettingsPage />
    {/if}

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 19. SYSTEMADMINISTRATION & DATENQUALITÄT                   -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    {#if currentPage === 'admin'}
      <AdminPage />
    {/if}

  </main>
</div>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- GLOBALE MODALS & DRAWERS                                    -->
<!-- ═══════════════════════════════════════════════════════════ -->
<QuickLogModal
  open={isQuickLogOpen}
  onclose={() => isQuickLogOpen = false}
  onsubmitwater={handleWaterSubmit}
  onopenbarcode={() => isBarcodeModalOpen = true}
/>

<CommandPalette
  open={isCmdKOpen}
  onclose={() => isCmdKOpen = false}
  onnavigate={navigateTo}
/>

<ConflictResolverModal
  open={isConflictModalOpen}
  onclose={() => isConflictModalOpen = false}
/>

<BarcodeScannerModal
  open={isBarcodeModalOpen}
  onclose={() => isBarcodeModalOpen = false}
/>

<ClinicalPdfReportModal
  open={isPdfModalOpen}
  onclose={() => isPdfModalOpen = false}
/>

<NotificationDrawer
  open={isNotificationDrawerOpen}
  onclose={() => isNotificationDrawerOpen = false}
/>

<OnboardingModal
  open={isOnboardingOpen}
  onclose={() => isOnboardingOpen = false}
/>

<!-- Dynamic Widget Gallery & Group Modals -->
<WidgetGalleryModal
  open={isGalleryOpen}
  targetGroup={activeGroupForGallery}
  onaddwidget={handleAddWidget}
  oncreategroup={openCreateGroup}
  onclose={() => isGalleryOpen = false}
/>

{#if isGroupEditorOpen && activeGroupForEdit}
  <WidgetGroupEditorModal
    open={isGroupEditorOpen}
    group={activeGroupForEdit}
    isNew={isCreatingNewGroup}
    onsave={handleSaveGroup}
    ondelete={handleDeleteGroup}
    onclose={() => isGroupEditorOpen = false}
  />
{/if}

<style>
  @keyframes iosWiggleEven {
    0% { transform: rotate(-0.4deg) translate(-0.3px, 0); }
    50% { transform: rotate(0.45deg) translate(0.3px, -0.3px); }
    100% { transform: rotate(-0.4deg) translate(-0.3px, 0); }
  }

  @keyframes iosWiggleOdd {
    0% { transform: rotate(0.45deg) translate(0.3px, 0); }
    50% { transform: rotate(-0.4deg) translate(-0.3px, 0.3px); }
    100% { transform: rotate(0.45deg) translate(0.3px, 0); }
  }

  .ios-wiggle-even {
    animation: iosWiggleEven 0.88s infinite ease-in-out;
    transform-origin: 50% 50%;
  }

  .ios-wiggle-odd {
    animation: iosWiggleOdd 0.94s infinite ease-in-out;
    transform-origin: 50% 50%;
  }
</style>
