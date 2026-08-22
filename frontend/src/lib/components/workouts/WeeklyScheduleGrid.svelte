<script lang="ts">
  export interface ScheduleSlot {
    weekday: number; // 0=Mo .. 6=So
    workoutId: string;
    name: string;
    exercisesCount?: number;
  }

  interface Props {
    slots?: ScheduleSlot[];
    interactive?: boolean;
  }

  let { slots = [], interactive = true }: Props = $props();

  const daysOfWeek = [
    { short: 'Mo', label: 'Montag' },
    { short: 'Di', label: 'Dienstag' },
    { short: 'Mi', label: 'Mittwoch' },
    { short: 'Do', label: 'Donnerstag' },
    { short: 'Fr', label: 'Freitag' },
    { short: 'Sa', label: 'Samstag' },
    { short: 'So', label: 'Sonntag' }
  ];

  const now = new Date();
  const currentWeekday = (now.getDay() + 6) % 7; // ISO 0=Monday .. 6=Sunday
</script>

<div class="grid grid-cols-2 gap-2.5 select-none sm:grid-cols-4 lg:grid-cols-7">
  {#each daysOfWeek as day, idx}
    {@const isToday = idx === currentWeekday}
    {@const daySlots = slots.filter((s) => s.weekday === idx)}
    {@const hasWorkout = daySlots.length > 0}

    <div
      class="relative flex flex-col justify-between rounded-2xl border p-3 transition-all {isToday
        ? 'border-primary bg-surface-0 shadow-sm ring-2 ring-primary/25'
        : hasWorkout
          ? 'border-border-subtle bg-surface-50/90'
          : 'border-border-subtle/60 bg-surface-100/40'}"
      style={!hasWorkout
        ? 'background-image: repeating-linear-gradient(-45deg, transparent, transparent 6px, rgba(120, 120, 120, 0.06) 6px, rgba(120, 120, 120, 0.06) 12px);'
        : ''}
    >
      <!-- Day Header -->
      <div class="flex items-center justify-between">
        <span
          class="font-mono text-xs font-black tracking-wider uppercase {isToday
            ? 'text-primary'
            : hasWorkout
              ? 'text-text-main'
              : 'text-text-muted/70'}"
        >
          {day.short}
        </span>

        {#if isToday}
          <span
            class="py-0.2 inline-flex items-center gap-1 rounded-full bg-primary px-1.5 text-[9px] font-black tracking-wide text-white uppercase shadow-2xs"
          >
            Heute
          </span>
        {/if}
      </div>

      <!-- Day Slot Content -->
      <div class="mt-2.5 flex min-h-[44px] flex-col justify-center">
        {#if hasWorkout}
          <div class="space-y-1.5">
            {#each daySlots as slot}
              {#if interactive}
                <a
                  href="/workouts/plans/{slot.workoutId}"
                  class="group block rounded-xl border border-primary/20 bg-primary-soft/30 p-2 text-left no-underline transition-all hover:border-primary hover:bg-primary-soft/60 active:scale-[0.98]"
                  title={slot.name}
                >
                  <span
                    class="block truncate text-xs font-extrabold text-primary transition-colors group-hover:underline"
                  >
                    {slot.name}
                  </span>
                  {#if slot.exercisesCount !== undefined}
                    <span class="mt-0.5 block text-[10px] font-medium text-text-muted">
                      {slot.exercisesCount} Übungen
                    </span>
                  {/if}
                </a>
              {:else}
                <div class="rounded-xl border border-primary/20 bg-primary-soft/30 p-2 text-left">
                  <span class="block truncate text-xs font-extrabold text-primary">
                    {slot.name}
                  </span>
                  {#if slot.exercisesCount !== undefined}
                    <span class="mt-0.5 block text-[10px] font-medium text-text-muted">
                      {slot.exercisesCount} Übungen
                    </span>
                  {/if}
                </div>
              {/if}
            {/each}
          </div>
        {:else}
          <!-- Rest Day: Clean hatched pattern with subtle dot/dash -->
          <div class="flex items-center justify-center py-2">
            <span class="h-1 w-4 rounded-full bg-border-subtle opacity-70"></span>
          </div>
        {/if}
      </div>
    </div>
  {/each}
</div>
