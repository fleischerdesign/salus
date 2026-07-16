<script lang="ts">
  import { liveQuery } from 'dexie';
  import { generateInsight } from '$lib/mutations/misc';
  import type { components } from '$lib/api/schema';
  import { db } from '$lib/db/database';
  import type { Insight } from '$lib/db/types';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import ListItem from '$components/ui/ListItem.svelte';

  let date = $state(new Date().toISOString().slice(0, 10));
  let generating = $state(false);

  let insight = liveQuery(() =>
    db.insight
      .where('query_date')
      .equals(date)
      .first()
      .then((i) => (i && !i.deleted_at ? i : null))
  );

  let history = liveQuery(() =>
    db.insight
      .toArray()
      .then((arr) =>
        arr
          .filter((i) => !i.deleted_at)
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      )
  );

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
    iconColor="#4f46e5"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch divide-x divide-surface-200 select-none">
        <!-- Date Selector Segment -->
        <div class="relative flex h-full items-center bg-surface-50/20 px-4">
          <input
            type="date"
            bind:value={date}
            class="h-full w-full border-0 bg-transparent text-sm text-surface-900 focus:ring-2 focus:ring-primary-500 focus:outline-none focus:ring-inset"
          />
        </div>

        <!-- Generate Segment -->
        <button
          type="button"
          disabled={generating}
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white transition-colors hover:bg-primary-600 active:bg-primary-700 disabled:opacity-50"
          onclick={generate}
        >
          {#if generating}
            <div
              class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
            ></div>
            <span>Generating…</span>
          {:else}
            <Icon name="auto-awesome" size="sm" />
            <span>Generate</span>
          {/if}
        </button>
      </div>
    {/snippet}
  </PageHeader>

  <div class="grid gap-6 lg:grid-cols-3">
    <div class="lg:col-span-2">
      {#if generating}
        <Card padding={false}>
          <div class="h-1 bg-gradient-to-r from-primary-500 to-primary-600"></div>
          <div class="space-y-4 p-6">
            <div class="flex items-center gap-3">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600"
              >
                <Icon name="psychology" size="sm" />
              </div>
              <div>
                <p class="text-sm font-semibold text-surface-900">AI Coach Health Insight</p>
                <p class="text-xs text-surface-400">Analyzing health telemetry...</p>
              </div>
            </div>
            <div class="animate-pulse space-y-3">
              <div class="h-3 w-1/2 rounded bg-surface-200"></div>
              <div class="h-3 w-full rounded bg-surface-100"></div>
              <div class="h-3 w-4/5 rounded bg-surface-100"></div>
              <div class="h-3 w-3/4 rounded bg-surface-100"></div>
            </div>
            <div class="animate-pulse space-y-3 pt-2">
              <div class="h-3 w-2/5 rounded bg-surface-200"></div>
              <div class="h-3 w-full rounded bg-surface-100"></div>
              <div class="h-3 w-5/6 rounded bg-surface-100"></div>
            </div>
          </div>
        </Card>
      {:else if $insight}
        <Card padding={false}>
          <div class="h-1 bg-gradient-to-r from-primary-500 to-primary-600"></div>
          <div class="px-6 pt-5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600"
                >
                  <Icon name="psychology" size="sm" />
                </div>
                <div>
                  <p class="text-sm font-semibold text-surface-900">AI Coach Health Insight</p>
                  <p class="text-xs text-surface-400">Daily telemetry evaluation</p>
                </div>
              </div>
              <span
                class="rounded-full bg-surface-100 px-2.5 py-0.5 text-xs font-medium text-surface-500"
              >
                {$insight.query_date}
              </span>
            </div>
          </div>
          <div class="px-6 py-4">
            <div class="text-sm leading-relaxed text-surface-700">
              {@html renderMarkdown($insight.content)}
            </div>
          </div>
          <div class="flex items-center justify-between border-t border-surface-100 px-6 py-3">
            <span class="text-xs text-surface-400">
              Model:
              <code class="rounded bg-surface-50 px-1 py-0.5 text-[11px] text-surface-500">
                {$insight.model_used}
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
              class="flex h-14 w-14 items-center justify-center rounded-full bg-surface-100 text-surface-400"
            >
              <Icon name="psychology" size="xl" />
            </div>
            <h3 class="mt-4 text-sm font-semibold text-surface-900">No insight for this date</h3>
            <p class="mt-1 text-xs text-surface-500">
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
            <span class="text-sm font-semibold text-surface-900">History</span>
          </div>
        {/snippet}

        {#if !$history}
          <div class="px-4 py-8 text-center">
            <p class="text-sm text-surface-400">Loading...</p>
          </div>
        {:else if $history.length > 0}
          <div class="divide-y divide-surface-100">
            {#each $history as item (item.id)}
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
                      <span class="text-xs font-semibold text-surface-700">
                        {item.query_date}
                      </span>
                      <span
                        class="shrink-0 rounded bg-surface-100 px-1.5 py-0.5 text-[10px] font-medium text-surface-500"
                      >
                        {(item.model_used ?? '').split('/').pop()}
                      </span>
                    </div>
                    <span class="mt-0.5 truncate text-xs text-surface-400">
                      {preview}
                    </span>
                  </button>
                {/snippet}
              </ListItem>
            {/each}
          </div>
        {:else}
          <div class="px-4 py-8 text-center">
            <p class="text-sm text-surface-400">No history yet.</p>
          </div>
        {/if}
      </Card>
    </div>
  </div>
</div>
