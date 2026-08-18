<script lang="ts">
  import Icon from '../ui/Icon.svelte';
  import Badge from '../ui/Badge.svelte';
  import DatePickerPopup from '../ui/DatePickerPopup.svelte';

  let {
    selectedDate = $bindable('2026-08-17'),
    todayDate = '2026-08-17'
  } = $props<{
    selectedDate: string;
    todayDate?: string;
  }>();

  let isDatePickerOpen = $state(false);

  let formattedDate = $derived.by(() => {
    const [y, m, d] = selectedDate.split('-').map(Number);
    if (!y || !m || !d) return selectedDate;
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString('de-DE', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  });

  let isToday = $derived(selectedDate === todayDate);

  let dayDeltaText = $derived.by(() => {
    const [y1, m1, d1] = selectedDate.split('-').map(Number);
    const [y2, m2, d2] = todayDate.split('-').map(Number);
    const date1 = new Date(y1, m1 - 1, d1);
    const date2 = new Date(y2, m2 - 1, d2);
    const diffTime = date1.getTime() - date2.getTime();
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Heute';
    if (diffDays === -1) return 'Gestern';
    if (diffDays === -2) return 'Vorgestern';
    if (diffDays < 0) return `Vor ${Math.abs(diffDays)} Tagen`;
    if (diffDays === 1) return 'Morgen';
    return `In ${diffDays} Tagen`;
  });

  function changeDay(delta: number) {
    const [y, m, d] = selectedDate.split('-').map(Number);
    const date = new Date(y, m - 1, d + delta);
    const ny = date.getFullYear();
    const nm = String(date.getMonth() + 1).padStart(2, '0');
    const nd = String(date.getDate()).padStart(2, '0');
    selectedDate = `${ny}-${nm}-${nd}`;
  }

  function jumpToToday() {
    selectedDate = todayDate;
  }
</script>

<div class="relative inline-flex items-center gap-2 bg-[var(--bg-surface-0)] border border-[var(--border-subtle)] rounded-2xl p-1.5 shadow-[var(--shadow-card)] flex-wrap sm:flex-nowrap">
  <!-- Previous Day Button -->
  <button
    type="button"
    onclick={() => changeDay(-1)}
    class="w-8 h-8 rounded-xl bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer transition-colors shrink-0"
    title="Vorheriger Tag"
  >
    <Icon name="chevron-left" size={16} />
  </button>

  <!-- Interactive Date Center Button (Opens Custom Glassmorphism Datepicker Popup) -->
  <button
    type="button"
    onclick={() => isDatePickerOpen = !isDatePickerOpen}
    class="flex-1 flex items-center justify-center gap-2 px-3 py-1.5 rounded-xl hover:bg-[var(--bg-surface-50)] cursor-pointer transition-colors text-center group"
    title="Kalender öffnen"
  >
    <Icon name="sun" size={16} class="text-[var(--color-primary)] shrink-0" />
    <div class="flex items-center gap-2 flex-wrap justify-center">
      <span class="text-xs sm:text-sm font-extrabold text-[var(--text-main)] tracking-tight">
        {formattedDate}
      </span>
      <Badge variant={isToday ? 'success' : 'default'} class="text-[0.6875rem]">
        {dayDeltaText}
      </Badge>
    </div>
    <Icon name="chevron-down" size={14} class="text-[var(--text-soft)] group-hover:text-[var(--text-main)] transition-transform {isDatePickerOpen ? 'rotate-180' : ''}" />
  </button>

  <!-- Next Day Button -->
  <button
    type="button"
    onclick={() => changeDay(1)}
    class="w-8 h-8 rounded-xl bg-[var(--bg-surface-50)] hover:bg-[var(--bg-surface-100)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--text-main)] flex items-center justify-center cursor-pointer transition-colors shrink-0"
    title="Nächster Tag"
  >
    <Icon name="chevron-right" size={16} />
  </button>

  <!-- Jump to Today Quick Button (if not on today) -->
  {#if !isToday}
    <button
      type="button"
      onclick={jumpToToday}
      class="px-2.5 py-1.5 rounded-xl bg-[var(--color-primary-soft)] text-[var(--color-primary)] font-bold text-xs hover:bg-[var(--color-primary)] hover:text-white cursor-pointer transition-all shrink-0"
    >
      Heute
    </button>
  {/if}

  <!-- CUSTOM DATEPICKER POPUP -->
  <DatePickerPopup
    open={isDatePickerOpen}
    value={selectedDate}
    today={todayDate}
    onselect={(d) => selectedDate = d}
    onclose={() => isDatePickerOpen = false}
  />
</div>
