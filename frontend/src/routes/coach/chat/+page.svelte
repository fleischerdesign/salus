<script lang="ts">
  import { generateInsight } from '$lib/mutations/misc';
  import { db } from '$lib/db/database';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ListItem from '$components/ui/ListItem.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';

  let date = $state(new Date().toISOString().slice(0, 10));
  let generating = $state(false);

  const insightQuery = useQuery(
    () =>
      db.insight
        .where('query_date')
        .equals(date)
        .first()
        .then((i) => (i && !i.deleted_at ? i : null)),
    () => date
  );
  const insight = $derived(insightQuery.value);

  const historyQuery = useQuery(() =>
    db.insight
      .toArray()
      .then((arr) =>
        arr
          .filter((i) => !i.deleted_at)
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      )
  );
  const history = $derived(historyQuery.value);

  async function generate() {
    generating = true;
    await generateInsight(date);
    generating = false;
  }

  function renderMarkdown(md: string): string {
    const esc = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return esc
      .replace(
        /^### (.+)$/gm,
        '<h3 class="mt-5 mb-2 text-sm font-semibold text-surface-900">$1</h3>'
      )
      .replace(
        /^## (.+)$/gm,
        '<h2 class="mt-5 mb-2 text-base font-semibold text-surface-900">$1</h2>'
      )
      .replace(
        /^# (.+)$/gm,
        '<h2 class="mt-5 mb-2 text-base font-semibold text-surface-900">$1</h2>'
      )
      .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-surface-900">$1</strong>')
      .replace(/^- (.+)$/gm, '<li class="ml-4 list-disc text-sm text-surface-600">$1</li>')
      .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal text-sm text-surface-600">$1</li>')
      .replace(/(<li[^>]*>.*?<\/li>\n?)+/g, (m) => `<ul class="my-2 space-y-1">${m}</ul>`)
      .replace(
        /^(?!<[hul])(.+)$/gm,
        '<p class="mb-2 text-sm leading-relaxed text-surface-600">$1</p>'
      )
      .replace(/\n{2,}/g, '\n');
  }
</script>

<svelte:head><title>Salus — AI Coach</title></svelte:head>

<div class="space-y-6">
  <PageHeader
    title="AI Coach"
    subtitle="Physician-grade daily health recommendations powered by LLMs"
    icon="psychology"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch divide-x divide-[var(--border-subtle)] select-none">
        <!-- Date Selector Segment -->
        <div class="relative flex h-full items-center bg-[var(--bg-surface-50)]/40 px-3">
          <input
            type="date"
            bind:value={date}
            class="h-full w-full cursor-pointer border-0 bg-transparent text-xs font-bold text-[var(--text-main)] focus:outline-none"
          />
        </div>

        <!-- Generate Segment -->
        <PageHeaderAction icon="auto-awesome" disabled={generating} onclick={generate}>
          {generating ? 'Generiere Empfehlungen…' : 'Neu generieren'}
        </PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2">
      {#if generating}
        <Card padding={false}>
          <div class="from-primary-500 to-primary-600 h-1 bg-gradient-to-r"></div>
          <div class="space-y-4 p-6">
            <div class="flex items-center gap-3">
              <div
                class="bg-primary-100 text-primary-600 flex h-10 w-10 items-center justify-center rounded-lg"
              >
                <Icon name="psychology" size="sm" />
              </div>
              <div>
                <p class="text-surface-900 text-sm font-semibold">AI Coach Health Insight</p>
                <p class="text-surface-400 text-xs">Analyzing health telemetry...</p>
              </div>
            </div>
            <div class="animate-pulse space-y-3">
              <div class="bg-surface-200 h-3 w-1/2 rounded"></div>
              <div class="bg-surface-100 h-3 w-full rounded"></div>
              <div class="bg-surface-100 h-3 w-4/5 rounded"></div>
              <div class="bg-surface-100 h-3 w-3/4 rounded"></div>
            </div>
            <div class="animate-pulse space-y-3 pt-2">
              <div class="bg-surface-200 h-3 w-2/5 rounded"></div>
              <div class="bg-surface-100 h-3 w-full rounded"></div>
              <div class="bg-surface-100 h-3 w-5/6 rounded"></div>
            </div>
          </div>
        </Card>
      {:else if insight}
        <Card padding={false}>
          <div class="from-primary-500 to-primary-600 h-1 bg-gradient-to-r"></div>
          <div class="px-6 pt-5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="bg-primary-100 text-primary-600 flex h-10 w-10 items-center justify-center rounded-lg"
                >
                  <Icon name="psychology" size="sm" />
                </div>
                <div>
                  <p class="text-surface-900 text-sm font-semibold">AI Coach Health Insight</p>
                  <p class="text-surface-400 text-xs">Daily telemetry evaluation</p>
                </div>
              </div>
              <span
                class="bg-surface-100 text-surface-500 rounded-full px-2.5 py-0.5 text-xs font-medium"
              >
                {insight.query_date}
              </span>
            </div>
          </div>
          <div class="px-6 py-4">
            <div class="text-surface-700 text-sm leading-relaxed">
              <!-- renderMarkdown escapes the content before wrapping it in static tags -->
              <!-- eslint-disable-next-line svelte/no-at-html-tags -->
              {@html renderMarkdown(insight.content)}
            </div>
          </div>
          <div class="border-surface-100 flex items-center justify-between border-t px-6 py-3">
            <span class="text-surface-400 text-xs">
              Model:
              <code class="bg-surface-50 text-surface-500 rounded px-1 py-0.5 text-[10px]">
                {insight.model_used}
              </code>
            </span>
            <Btn variant="ghost" size="sm" loading={generating} onclick={generate}>
              <Icon name="refresh" size="sm" />Regenerate
            </Btn>
          </div>
        </Card>
      {:else}
        <Card padding={false}>
          <div class="flex flex-col items-center py-16 text-center">
            <div
              class="bg-surface-100 text-surface-400 flex h-14 w-14 items-center justify-center rounded-full"
            >
              <Icon name="psychology" size="xl" />
            </div>
            <h3 class="text-surface-900 mt-4 text-sm font-semibold">No insight for this date</h3>
            <p class="text-surface-500 mt-1 text-xs">
              Click Generate to create an AI-powered health insight.
            </p>
            <div class="mt-6">
              <Btn variant="primary" size="sm" loading={generating} onclick={generate}>
                <Icon name="auto-awesome" size="sm" />Generate Insight
              </Btn>
            </div>
          </div>
        </Card>
      {/if}
    </div>

    <div class="lg:col-span-1">
      <Card padding={false}>
        {#snippet header()}
          <div class="flex items-center gap-2">
            <Icon name="history" size="sm" class="text-surface-400" />
            <span class="text-surface-900 text-sm font-semibold">History</span>
          </div>
        {/snippet}

        {#if !history}
          <div class="px-4 py-8 text-center">
            <p class="text-surface-400 text-sm">Loading...</p>
          </div>
        {:else if (history ?? []).length > 0}
          <div class="divide-surface-100 divide-y">
            {#each history ?? [] as item (item.id)}
              {@const preview = item.content.slice(0, 80)}
              <ListItem
                hoverable
                clickable
                divider={false}
                class={item.query_date === date ? 'bg-primary-50' : ''}
              >
                {#snippet children()}
                  <button
                    type="button"
                    class="flex w-full flex-col overflow-hidden text-left"
                    onclick={() => (date = item.query_date)}
                  >
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-surface-700 text-xs font-semibold">
                        {item.query_date}
                      </span>
                      <span
                        class="bg-surface-100 text-surface-500 shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium"
                      >
                        {(item.model_used ?? '').split('/').pop()}
                      </span>
                    </div>
                    <span class="text-surface-400 mt-0.5 truncate text-xs">
                      {preview}
                    </span>
                  </button>
                {/snippet}
              </ListItem>
            {/each}
          </div>
        {:else}
          <div class="px-4 py-8 text-center">
            <p class="text-surface-400 text-sm">No history yet.</p>
          </div>
        {/if}
      </Card>
    </div>
  </div>
</div>
