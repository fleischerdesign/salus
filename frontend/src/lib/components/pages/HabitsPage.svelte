<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import Btn from '../ui/Btn.svelte';
  import Modal from '../ui/Modal.svelte';
  import Input from '../ui/Input.svelte';
  import AchievementCard from '../gamification/AchievementCard.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { todayString } from '$lib/utils/datetime';
  import { toggleHabit, createHabit } from '$lib/mutations/wellness';

  const today = todayString();

  // 1. Reactive Composite Query for Habits + Today's Logs (Single liveQuery)
  const habitsQuery = useQuery(
    async () => {
      const [allHabits, allLogs] = await Promise.all([
        db.habit.toArray(),
        db.habit_log.where('log_date').equals(today).toArray()
      ]);

      const activeHabits = allHabits.filter((h) => !h.deleted_at && !h.is_archived);
      const completedMap = new Map(
        allLogs.filter((l) => !l.deleted_at).map((l) => [l.habit_id, l.completed])
      );

      return activeHabits.map((h) => ({
        id: h.id,
        title: h.name,
        category: h.description || 'Alltag',
        frequency: h.frequency || 'Täglich',
        color: h.color || 'var(--color-primary)',
        icon: h.icon || 'check',
        doneToday: Boolean(completedMap.get(h.id))
      }));
    },
    () => today
  );

  const habits = $derived(habitsQuery.value ?? []);
  const loading = $derived(habitsQuery.loading);

  let isCreateOpen = $state(false);
  let newName = $state('');
  let newCategory = $state('');

  async function handleCreate() {
    if (!newName.trim()) return;
    await createHabit({
      name: newName.trim(),
      description: newCategory.trim() || undefined,
      color: '#2563eb',
      icon: 'check',
      frequency: 'daily',
      target_count: 1
    });
    newName = '';
    newCategory = '';
    isCreateOpen = false;
  }

  async function handleToggle(habitId: string) {
    await toggleHabit(habitId);
  }
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-extrabold tracking-tight">Gewohnheiten & Habit-Management</h1>
      <p class="mt-0.5 text-sm text-[var(--text-muted)]">
        Wissenschaftliche Verhaltensarchitektur nach der 66-Tage-Automatisierungsregel
      </p>
    </div>
    <div class="flex items-center gap-2">
      {#if habits.length > 0}
        <Badge variant="success">
          {habits.filter((h) => h.doneToday).length} / {habits.length} heute erledigt
        </Badge>
      {/if}
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        + Gewohnheit anlegen
      </Btn>
    </div>
  </div>

  <!-- Habit Grid -->
  {#if loading}
    <div class="py-12 text-center text-sm text-[var(--text-muted)]">
      Gewohnheiten werden geladen...
    </div>
  {:else if habits.length === 0}
    <div
      class="space-y-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-8 text-center shadow-[var(--shadow-card)]"
    >
      <div
        class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-primary-soft)] text-[var(--color-primary)]"
      >
        <Icon name="checklist" size="lg" />
      </div>
      <div>
        <h3 class="text-base font-bold text-[var(--text-main)]">
          Noch keine Gewohnheiten angelegt
        </h3>
        <p class="mx-auto mt-1 max-w-sm text-xs text-[var(--text-muted)]">
          Baue gesunde Routinen auf. Lege Gewohnheiten wie Wassertrinken, Schritte oder
          Schlafhygiene an.
        </p>
      </div>
      <Btn variant="primary" size="sm" onclick={() => (isCreateOpen = true)}>
        Jetzt erste Gewohnheit anlegen
      </Btn>
    </div>
  {:else}
    <div class="space-y-4">
      {#each habits as h (h.id)}
        <div
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-5 shadow-[var(--shadow-card)]"
        >
          <div class="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-base font-bold text-[var(--text-main)]">{h.title}</span>
                <Badge variant="default" class="text-[0.625rem]">{h.category}</Badge>
              </div>
              <p class="mt-0.5 text-xs text-[var(--text-muted)]">Frequenz: {h.frequency}</p>
            </div>

            <div class="flex items-center gap-4">
              <button
                type="button"
                onclick={() => handleToggle(h.id)}
                class="flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-1.5 text-xs font-bold transition-all {h.doneToday
                  ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20'
                  : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
              >
                <Icon name={h.doneToday ? 'check-circle' : 'schedule'} size="sm" />
                <span>{h.doneToday ? 'Heute erledigt ✓' : 'Als erledigt markieren'}</span>
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Achievements Gallery -->
  <AchievementCard />

  <!-- Create Habit Modal -->
  <Modal
    open={isCreateOpen}
    title="Neue Gewohnheit erstellen"
    onclose={() => (isCreateOpen = false)}
  >
    <form
      onsubmit={(e) => {
        e.preventDefault();
        handleCreate();
      }}
      class="space-y-4"
    >
      <div>
        <label for="habit-name" class="mb-1 block text-xs font-bold text-[var(--text-main)]"
          >Name der Gewohnheit</label
        >
        <Input id="habit-name" bind:value={newName} placeholder="z. B. 3 Liter Wasser trinken" />
      </div>
      <div>
        <label for="habit-cat" class="mb-1 block text-xs font-bold text-[var(--text-main)]"
          >Kategorie / Notiz</label
        >
        <Input
          id="habit-cat"
          bind:value={newCategory}
          placeholder="z. B. Hydration & Stoffwechsel"
        />
      </div>
      <div class="flex justify-end gap-2 pt-2">
        <Btn variant="secondary" size="sm" onclick={() => (isCreateOpen = false)}>Abbrechen</Btn>
        <Btn variant="primary" size="sm" type="submit" disabled={!newName.trim()}>Speichern</Btn>
      </div>
    </form>
  </Modal>
</div>
