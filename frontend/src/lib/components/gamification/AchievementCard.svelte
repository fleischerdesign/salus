<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import { db } from '$lib/db/database';
  import { useQuery } from '$lib/db/use-query.svelte';

  const achievementsQuery = useQuery(async () => {
    const [definitions, userAchievements] = await Promise.all([
      db.achievement_definition.toArray(),
      db.user_achievement.toArray()
    ]);

    const unlockedMap = new Map(userAchievements.map((ua) => [ua.achievement_code, ua]));

    return definitions
      .filter((d) => !d.is_hidden)
      .sort((a, b) => a.sort_order - b.sort_order)
      .map((d) => {
        const userAch = unlockedMap.get(d.code);
        return {
          code: d.code,
          title: d.title,
          tier: d.tier || 'Gold',
          desc: d.description,
          icon: d.icon || 'emoji_events',
          unlocked: Boolean(userAch?.unlocked_at),
          progress: userAch?.progress_current ?? 0,
          max: userAch?.progress_target ?? 100
        };
      });
  });

  const achievements = $derived(achievementsQuery.value ?? []);
  const unlockedCount = $derived(achievements.filter((a) => a.unlocked).length);
</script>

<div class="rounded-2xl border border-border-subtle bg-surface-0 p-5 shadow-card">
  <div class="mb-4 flex items-center justify-between">
    <div class="flex items-center gap-1.5 text-sm font-bold text-text-main">
      <Icon name="emoji_events" class="text-circadian" />
      <span>Akademische Meilensteine und Erfolge</span>
    </div>
    <Badge variant="fasting" class="!bg-circadian-soft !text-circadian">
      {unlockedCount} / {achievements.length} Freigeschaltet
    </Badge>
  </div>

  {#if achievements.length === 0}
    <div class="space-y-2 py-8 text-center text-xs text-text-muted">
      <Icon name="emoji_events" size="lg" class="mx-auto text-text-muted opacity-60" />
      <p class="text-xs font-bold text-text-main">Noch keine Erfolge hinterlegt</p>
      <p class="mx-auto max-w-sm text-[0.6875rem]">
        Erfasse regelmäßig deine Gesundheitsdaten und baue Routinen auf, um Meilensteine zu
        erreichen.
      </p>
    </div>
  {:else}
    <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {#each achievements as ach (ach.code)}
        <div
          class="flex flex-col justify-between rounded-xl border border-border-subtle bg-surface-50 p-3.5 {ach.unlocked
            ? 'border-circadian/30'
            : 'opacity-70'}"
        >
          <div class="mb-2 flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-xs font-bold text-text-main">{ach.title}</span>
                <Badge variant={ach.unlocked ? 'success' : 'default'} class="text-[0.625rem]">
                  {ach.tier}
                </Badge>
              </div>
              <p class="mt-1 text-[0.6875rem] text-text-muted">{ach.desc}</p>
            </div>
            <div
              class="flex h-8 w-8 items-center justify-center rounded-full {ach.unlocked
                ? 'bg-amber-400/20 text-amber-500'
                : 'bg-surface-100 text-text-muted'} shrink-0"
            >
              <Icon name={ach.icon} size="sm" />
            </div>
          </div>

          <div class="space-y-1 border-t border-border-subtle pt-2">
            <div class="flex justify-between font-mono text-[0.625rem] text-text-muted">
              <span>{ach.unlocked ? 'Erreicht ✓' : 'Fortschritt'}</span>
              <span>{ach.progress} / {ach.max}</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-surface-100">
              <div
                class="h-full bg-circadian transition-all"
                style="width: {Math.min(100, Math.round((ach.progress / (ach.max || 1)) * 100))}%"
              ></div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
