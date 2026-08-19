<script lang="ts">
  import Icon from './Icon.svelte';

  let {
    value = '2026-08-17',
    today = '2026-08-17',
    open = false,
    onselect,
    onclose
  } = $props<{
    value: string;
    today?: string;
    open: boolean;
    onselect: (dateStr: string) => void;
    onclose: () => void;
  }>();

  // Internal view state for month/year browsing
  let viewYear = $state(2026);
  let viewMonth = $state(7); // 0-indexed (August)

  // Sync internal view when value changes
  $effect(() => {
    if (value) {
      const [y, m] = value.split('-').map(Number);
      if (y && m) {
        viewYear = y;
        viewMonth = m - 1;
      }
    }
  });

  const monthNames = [
    'Januar',
    'Februar',
    'März',
    'April',
    'Mai',
    'Juni',
    'Juli',
    'August',
    'September',
    'Oktober',
    'November',
    'Dezember'
  ];

  const weekdayNames = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  interface CalendarDay {
    dateStr: string;
    dayNum: number;
    isCurrentMonth: boolean;
    isToday: boolean;
    isSelected: boolean;
  }

  let calendarDays = $derived.by<CalendarDay[]>(() => {
    const days: CalendarDay[] = [];

    // First day of current view month
    const firstDay = new Date(viewYear, viewMonth, 1);
    let startDayOfWeek = firstDay.getDay() - 1;
    if (startDayOfWeek === -1) startDayOfWeek = 6;

    // Days in previous month
    const prevMonthLastDate = new Date(viewYear, viewMonth, 0).getDate();
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const d = prevMonthLastDate - i;
      const pm = viewMonth === 0 ? 12 : viewMonth;
      const py = viewMonth === 0 ? viewYear - 1 : viewYear;
      const dateStr = `${py}-${String(pm).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      days.push({
        dateStr,
        dayNum: d,
        isCurrentMonth: false,
        isToday: dateStr === today,
        isSelected: dateStr === value
      });
    }

    // Days in current month
    const daysInCurrentMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
    for (let d = 1; d <= daysInCurrentMonth; d++) {
      const m = viewMonth + 1;
      const dateStr = `${viewYear}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      days.push({
        dateStr,
        dayNum: d,
        isCurrentMonth: true,
        isToday: dateStr === today,
        isSelected: dateStr === value
      });
    }

    // Days in next month to fill complete 6-row grid (42 cells)
    const remaining = 42 - days.length;
    for (let d = 1; d <= remaining; d++) {
      const nm = viewMonth === 11 ? 1 : viewMonth + 2;
      const ny = viewMonth === 11 ? viewYear + 1 : viewYear;
      const dateStr = `${ny}-${String(nm).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      days.push({
        dateStr,
        dayNum: d,
        isCurrentMonth: false,
        isToday: dateStr === today,
        isSelected: dateStr === value
      });
    }

    return days;
  });

  function prevMonth() {
    if (viewMonth === 0) {
      viewMonth = 11;
      viewYear -= 1;
    } else {
      viewMonth -= 1;
    }
  }

  function nextMonth() {
    if (viewMonth === 11) {
      viewMonth = 0;
      viewYear += 1;
    } else {
      viewMonth += 1;
    }
  }

  function pickDay(dateStr: string) {
    onselect(dateStr);
    onclose();
  }

  function setRelative(offsetDays: number) {
    const date = new Date(today);
    date.setDate(date.getDate() + offsetDays);
    const ny = date.getFullYear();
    const nm = String(date.getMonth() + 1).padStart(2, '0');
    const nd = String(date.getDate()).padStart(2, '0');
    pickDay(`${ny}-${nm}-${nd}`);
  }
</script>

{#if open}
  <!-- Invisible Click Catcher (No Dark Backdrop / No Blur) -->
  <div class="fixed inset-0 z-55 bg-transparent" onclick={onclose} role="presentation"></div>

  <!-- Glassmorphism Calendar Popover -->
  <div
    class="glass-panel animate-modal-pop fixed top-24 left-1/2 z-56 w-[330px] -translate-x-1/2 space-y-3.5 rounded-3xl p-4 text-text-main shadow-dock sm:absolute sm:top-14 sm:right-0 sm:left-auto sm:translate-x-0"
  >
    <!-- Header: Month / Year Navigation -->
    <div class="flex items-center justify-between px-1">
      <div>
        <h3 class="text-sm font-extrabold text-text-main">
          {monthNames[viewMonth]}
          <span class="font-semibold text-text-muted">{viewYear}</span>
        </h3>
      </div>

      <div class="flex items-center gap-1">
        <button
          type="button"
          onclick={prevMonth}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-text-muted transition-colors hover:bg-surface-50 hover:text-text-main"
          title="Vorheriger Monat"
        >
          <Icon name="chevron-left" size={16} />
        </button>

        <button
          type="button"
          onclick={nextMonth}
          class="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-text-muted transition-colors hover:bg-surface-50 hover:text-text-main"
          title="Nächster Monat"
        >
          <Icon name="chevron-right" size={16} />
        </button>
      </div>
    </div>

    <!-- Weekday Labels Header -->
    <div
      class="grid grid-cols-7 gap-1 text-center text-[0.625rem] font-bold text-text-soft select-none"
    >
      {#each weekdayNames as wd}
        <div>{wd}</div>
      {/each}
    </div>

    <!-- 7x6 Calendar Grid -->
    <div class="grid grid-cols-7 gap-1 text-xs">
      {#each calendarDays as day}
        <button
          type="button"
          onclick={() => pickDay(day.dateStr)}
          class="relative flex h-8 cursor-pointer items-center justify-center rounded-xl font-semibold transition-all select-none
            {day.isSelected
            ? 'z-10 scale-105 bg-primary font-extrabold text-white shadow-sm'
            : day.isToday
              ? 'border-2 border-primary font-bold text-primary'
              : day.isCurrentMonth
                ? 'text-text-main hover:bg-surface-50'
                : 'text-text-soft/60 hover:bg-surface-50/40 hover:text-text-soft'}"
        >
          <span>{day.dayNum}</span>
        </button>
      {/each}
    </div>

    <!-- Quick Date Shortcuts Row -->
    <div class="flex items-center justify-between gap-1.5 border-t border-border-subtle pt-2">
      <button
        type="button"
        onclick={() => setRelative(0)}
        class="flex-1 cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1 text-center text-[0.6875rem] font-bold text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
      >
        Heute
      </button>

      <button
        type="button"
        onclick={() => setRelative(-1)}
        class="flex-1 cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1 text-center text-[0.6875rem] font-bold text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
      >
        Gestern
      </button>

      <button
        type="button"
        onclick={() => setRelative(-7)}
        class="flex-1 cursor-pointer rounded-xl border border-border-subtle bg-surface-50 px-2 py-1 text-center text-[0.6875rem] font-bold text-text-muted transition-colors hover:bg-surface-100 hover:text-text-main"
      >
        -7 Tage
      </button>
    </div>
  </div>
{/if}
