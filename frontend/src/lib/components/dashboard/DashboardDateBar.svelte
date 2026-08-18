<script lang="ts">
  import Icon from '$components/ui/Icon.svelte';
  import Badge from '$components/ui/Badge.svelte';
  import DatePickerPopup from '$components/ui/DatePickerPopup.svelte';
  import { todayString } from '$lib/utils/datetime';

  let {
    selectedDate = $bindable(todayString()),
    todayDate = todayString(),
    isEditMode = false,
    ontoggleedit,
    onaddwidget,
    onreset
  } = $props<{
    selectedDate: string;
    todayDate?: string;
    isEditMode?: boolean;
    ontoggleedit?: () => void;
    onaddwidget?: () => void;
    onreset?: () => void;
  }>();

  let isDatePickerOpen = $state(false);

  // Full long format for large desktop screens: "Dienstag, 18. August 2026"
  let fullFormattedDate = $derived.by(() => {
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

  // Medium compact format for laptops/tablets: "Di., 18. Aug. 2026"
  let mediumFormattedDate = $derived.by(() => {
    const [y, m, d] = selectedDate.split('-').map(Number);
    if (!y || !m || !d) return selectedDate;
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString('de-DE', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  });

  // Short format for mobile phones: "Di., 18. Aug."
  let shortFormattedDate = $derived.by(() => {
    const [y, m, d] = selectedDate.split('-').map(Number);
    if (!y || !m || !d) return selectedDate;
    const date = new Date(y, m - 1, d);
    return date.toLocaleDateString('de-DE', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
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
    if (diffDays === 1) return 'Morgen';
    if (diffDays > 1) return `+${diffDays}T`;
    return `${diffDays}T`;
  });

  function changeDay(offset: number) {
    const [y, m, d] = selectedDate.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    date.setDate(date.getDate() + offset);
    const ny = date.getFullYear();
    const nm = String(date.getMonth() + 1).padStart(2, '0');
    const nd = String(date.getDate()).padStart(2, '0');
    selectedDate = `${ny}-${nm}-${nd}`;
  }
</script>

<div
  class="relative flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-surface-0)] p-2 shadow-xs sm:p-2.5"
>
  <!-- Left: Date Navigator Pill -->
  <div class="flex min-w-0 flex-1 items-center gap-1 sm:gap-1.5">
    <!-- Previous Day Button -->
    <button
      type="button"
      onclick={() => changeDay(-1)}
      class="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-surface-100)] hover:text-[var(--text-main)]"
      title="Vorheriger Tag"
      aria-label="Vorheriger Tag"
    >
      <Icon name="chevron-left" size={16} />
    </button>

    <!-- Date Display Pill (Click opens DatePicker Popup) -->
    <button
      type="button"
      onclick={() => (isDatePickerOpen = !isDatePickerOpen)}
      class="group flex min-w-0 flex-1 cursor-pointer items-center justify-between overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2.5 py-1.5 text-left transition-all hover:bg-[var(--bg-surface-100)] sm:px-3"
    >
      <div class="flex min-w-0 items-center gap-1.5 truncate sm:gap-2">
        <Icon name="wb-sunny" size={16} class="shrink-0 text-[var(--color-primary)]" />

        <!-- Responsive date string based on viewport width -->
        <span
          class="hidden truncate text-xs font-extrabold tracking-tight text-[var(--text-main)] sm:text-sm lg:inline"
        >
          {fullFormattedDate}
        </span>
        <span
          class="hidden truncate text-xs font-extrabold tracking-tight text-[var(--text-main)] sm:inline sm:text-sm lg:hidden"
        >
          {mediumFormattedDate}
        </span>
        <span
          class="inline truncate text-xs font-extrabold tracking-tight text-[var(--text-main)] sm:hidden"
        >
          {shortFormattedDate}
        </span>

        <Badge
          variant={isToday ? 'success' : 'default'}
          class="shrink-0 px-1.5 py-0.5 text-[0.625rem] sm:text-[0.6875rem]"
        >
          {dayDeltaText}
        </Badge>
      </div>

      <Icon
        name="expand-more"
        size={14}
        class="ml-1 shrink-0 text-[var(--text-soft)] transition-transform group-hover:text-[var(--text-main)] {isDatePickerOpen
          ? 'rotate-180'
          : ''}"
      />
    </button>

    <!-- Next Day Button -->
    <button
      type="button"
      onclick={() => changeDay(1)}
      class="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] transition-colors hover:bg-[var(--bg-surface-100)] hover:text-[var(--text-main)]"
      title="Nächster Tag"
      aria-label="Nächster Tag"
    >
      <Icon name="chevron-right" size={16} />
    </button>
  </div>

  <!-- Right: Dashboard Layout Controls -->
  {#if ontoggleedit}
    <div class="flex shrink-0 items-center gap-1 sm:gap-1.5">
      {#if isEditMode}
        {#if onaddwidget}
          <button
            type="button"
            onclick={onaddwidget}
            class="flex cursor-pointer items-center gap-1.5 rounded-xl bg-[var(--color-primary)] px-2.5 py-1.5 text-xs font-bold text-white shadow-xs transition-all hover:opacity-90 sm:px-3"
            title="Widget oder Gruppe hinzufügen"
          >
            <Icon name="add" size="sm" />
            <span>Hinzufügen</span>
          </button>
        {/if}

        {#if onreset}
          <button
            type="button"
            onclick={onreset}
            class="flex cursor-pointer items-center gap-1 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-surface-50)] px-2.5 py-1.5 text-xs font-semibold text-rose-500 transition-colors hover:border-rose-500/30 hover:bg-rose-500/10"
            title="Auf Standard zurücksetzen"
          >
            <span>Reset</span>
          </button>
        {/if}
      {/if}

      <button
        type="button"
        onclick={ontoggleedit}
        class="flex cursor-pointer items-center gap-1.5 rounded-xl border px-2.5 py-1.5 text-xs font-bold transition-all sm:px-3 {isEditMode
          ? 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-main)] hover:bg-[var(--bg-surface-100)]'
          : 'border-[var(--border-subtle)] bg-[var(--bg-surface-50)] text-[var(--text-muted)] hover:text-[var(--text-main)]'}"
      >
        <Icon name={isEditMode ? 'check' : 'tune'} size="sm" />
        <span class="hidden sm:inline">{isEditMode ? 'Fertig' : 'Layout'}</span>
      </button>
    </div>
  {/if}

  <!-- CUSTOM DATEPICKER POPUP -->
  <DatePickerPopup
    open={isDatePickerOpen}
    value={selectedDate}
    today={todayDate}
    onselect={(d) => (selectedDate = d)}
    onclose={() => (isDatePickerOpen = false)}
  />
</div>
