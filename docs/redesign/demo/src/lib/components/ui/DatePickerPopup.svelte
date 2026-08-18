<script lang="ts">
  import Icon from './Icon.svelte';
  import Badge from './Badge.svelte';
  import Btn from './Btn.svelte';

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
    'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
    'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
  ];

  const weekdayNames = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];

  // Days with simulated biometric health records in local DB
  const loggedDays = new Set([
    '2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04', '2026-08-05',
    '2026-08-06', '2026-08-07', '2026-08-08', '2026-08-09', '2026-08-10',
    '2026-08-11', '2026-08-12', '2026-08-13', '2026-08-14', '2026-08-15',
    '2026-08-16', '2026-08-17'
  ]);

  interface CalendarDay {
    dateStr: string;
    dayNum: number;
    isCurrentMonth: boolean;
    isToday: boolean;
    isSelected: boolean;
    hasData: boolean;
  }

  let calendarDays = $derived.by<CalendarDay[]>(() => {
    const days: CalendarDay[] = [];
    
    // First day of current view month
    const firstDay = new Date(viewYear, viewMonth, 1);
    // Day of week (0 = Sun, 1 = Mon ... adjust so Mon = 0)
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
        isSelected: dateStr === value,
        hasData: loggedDays.has(dateStr)
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
        isSelected: dateStr === value,
        hasData: loggedDays.has(dateStr)
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
        isSelected: dateStr === value,
        hasData: loggedDays.has(dateStr)
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

  function quickJump(deltaDays: number) {
    const [y, m, d] = today.split('-').map(Number);
    const date = new Date(y, m - 1, d + deltaDays);
    const ny = date.getFullYear();
    const nm = String(date.getMonth() + 1).padStart(2, '0');
    const nd = String(date.getDate()).padStart(2, '0');
    pickDay(`${ny}-${nm}-${nd}`);
  }
</script>

{#if open}
  <!-- Invisible Click Catcher (No Dark Backdrop / No Blur) -->
  <div
    class="fixed inset-0 z-55 bg-transparent"
    onclick={onclose}
    role="presentation"
  ></div>

  <!-- Glassmorphism Calendar Popover -->
  <div
    class="fixed left-1/2 top-24 -translate-x-1/2 sm:absolute sm:left-auto sm:top-14 sm:right-0 sm:translate-x-0 z-56 w-[330px] glass-panel rounded-3xl p-4 shadow-[var(--shadow-dock)] text-[var(--text-main)] space-y-3.5 animate-modal-pop"
  >
    <!-- Header: Month / Year Navigation -->
    <div class="flex items-center justify-between px-1">
      <div>
        <h3 class="font-extrabold text-sm text-[var(--text-main)]">
          {monthNames[viewMonth]} <span class="font-semibold text-[var(--text-muted)]">{viewYear}</span>
        </h3>
      </div>

      <div class="flex items-center gap-1">
        <button
          type="button"
          onclick={prevMonth}
          class="w-7 h-7 rounded-lg bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer transition-colors"
          title="Vorheriger Monat"
        >
          <Icon name="chevron-left" size={14} />
        </button>
        <button
          type="button"
          onclick={nextMonth}
          class="w-7 h-7 rounded-lg bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-main)] cursor-pointer transition-colors"
          title="Nächster Monat"
        >
          <Icon name="chevron-right" size={14} />
        </button>
      </div>
    </div>

    <!-- Quick Presets Pills -->
    <div class="flex items-center gap-1.5 overflow-x-auto pb-0.5">
      <button
        type="button"
        onclick={() => quickJump(0)}
        class="px-2.5 py-1 rounded-lg text-[0.6875rem] font-bold cursor-pointer transition-all whitespace-nowrap {value === today ? 'bg-[var(--color-primary)] text-white' : 'bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] text-[var(--text-muted)]'}"
      >
        Heute
      </button>
      <button
        type="button"
        onclick={() => quickJump(-1)}
        class="px-2.5 py-1 rounded-lg text-[0.6875rem] font-bold bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] text-[var(--text-muted)] cursor-pointer transition-all whitespace-nowrap"
      >
        Gestern
      </button>
      <button
        type="button"
        onclick={() => quickJump(-7)}
        class="px-2.5 py-1 rounded-lg text-[0.6875rem] font-bold bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] text-[var(--text-muted)] cursor-pointer transition-all whitespace-nowrap"
      >
        Vor 7 Tagen
      </button>
    </div>

    <!-- Weekday Grid Header -->
    <div class="grid grid-cols-7 text-center text-[0.6875rem] font-bold text-[var(--text-soft)]">
      {#each weekdayNames as wd}
        <span class="py-0.5">{wd}</span>
      {/each}
    </div>

    <!-- 7x6 Calendar Days Grid -->
    <div class="grid grid-cols-7 gap-1 text-center">
      {#each calendarDays as d}
        <button
          type="button"
          onclick={() => pickDay(d.dateStr)}
          class="relative h-9 rounded-xl flex flex-col items-center justify-center text-xs font-semibold cursor-pointer transition-all select-none {d.isSelected
            ? 'bg-[var(--color-primary)] text-white font-extrabold shadow-sm scale-105 z-10'
            : d.isToday
            ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary)] font-bold border border-[var(--color-primary)]/40'
            : d.isCurrentMonth
            ? 'text-[var(--text-main)] hover:bg-[var(--bg-surface-50)]'
            : 'text-[var(--text-soft)] opacity-40 hover:opacity-80'}"
        >
          <span>{d.dayNum}</span>

          <!-- Health Data Point Indicator -->
          {#if d.hasData && !d.isSelected}
            <span class="absolute bottom-1 w-1 h-1 rounded-full bg-emerald-500"></span>
          {/if}
        </button>
      {/each}
    </div>

    <!-- Footer Legend -->
    <div class="pt-2 border-t border-[var(--border-subtle)] flex items-center justify-between text-[0.625rem] text-[var(--text-muted)]">
      <span class="flex items-center gap-1.5">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        Messdaten vorhanden
      </span>
      <button type="button" onclick={onclose} class="text-[var(--color-primary)] font-bold hover:underline cursor-pointer">
        Schließen
      </button>
    </div>

  </div>
{/if}
