<script lang="ts">
  import { api } from '$lib/api/client';
  import Card from '$components/ui/Card.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Textarea from '$components/ui/Textarea.svelte';
  import AlertBanner from '$components/ui/AlertBanner.svelte';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { db } from '$lib/db/database';

  let csv = $state('');
  let importing = $state(false);
  let message = $state<{ type: 'success' | 'error'; text: string } | null>(null);
  let preview = $state<string[]>([]);

  const foodsQuery = useQuery(() => db.food_item.count());
  const foodCount = $derived(foodsQuery.value ?? 0);

  interface ImportRow {
    name: string;
    serving_size: number;
    serving_unit: string;
    calories_per_serving: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    brand?: string;
    barcode?: string;
  }

  function parseCsv(text: string): ImportRow[] {
    return text
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [name, calories, protein, carbs, fat, brand = '', barcode = ''] = line
          .split(';')
          .map((c) => c.trim());
        return {
          name,
          serving_size: 100,
          serving_unit: 'g',
          calories_per_serving: parseFloat(calories) || 0,
          protein_g: parseFloat(protein) || 0,
          carbs_g: parseFloat(carbs) || 0,
          fat_g: parseFloat(fat) || 0,
          brand: brand || undefined,
          barcode: barcode || undefined
        };
      });
  }

  $effect(() => {
    preview = parseCsv(csv)
      .map((i) => i.name as string)
      .slice(0, 8);
  });

  async function handleImport() {
    const items = parseCsv(csv);
    if (items.length === 0) return;
    importing = true;
    message = null;
    try {
      const res = await api.POST('/api/v1/admin/foods/import', { body: { items } });
      if (res.data) {
        message = { type: 'success', text: `Imported ${res.data.imported} food items.` };
        csv = '';
      } else {
        message = { type: 'error', text: 'Import failed.' };
      }
    } catch {
      message = { type: 'error', text: 'Import failed — server error.' };
    } finally {
      importing = false;
    }
  }
</script>

<svelte:head><title>Salus — Food Database Import</title></svelte:head>

<div class="space-y-4">
  <AlertBanner variant="warning">
    Bulk-import curated foods as verified system items (shared with all users). Format per line: <code
      >name;calories;protein;carbs;fat;brand;barcode</code
    >. Idempotent — items with an existing barcode or name are skipped.
  </AlertBanner>

  <Card>
    <div class="flex items-center justify-between">
      <h2 class="text-sm font-semibold text-surface-900">Food Import</h2>
      <span class="text-xs text-surface-400">Current local DB: {foodCount} items</span>
    </div>
    <div class="mt-3">
      <Textarea
        name="food_csv"
        rows={10}
        placeholder={'Haferflocken;389;16.9;66.3;6.9;Alnatura\nMilch (3,5%);61;3.2;4.8;3.3'}
        bind:value={csv}
      />
    </div>
    {#if preview.length > 0}
      <p class="mt-2 text-xs text-surface-400">
        Preview: {preview.join(', ')}{parseCsv(csv).length > 8 ? ', …' : ''}
      </p>
    {/if}
    <div class="mt-4 flex items-center gap-3">
      <Btn
        variant="primary"
        onclick={handleImport}
        loading={importing}
        disabled={parseCsv(csv).length === 0}
      >
        Import {parseCsv(csv).length} Items
      </Btn>
      {#if message}
        <span class="text-sm {message.type === 'success' ? 'text-success-600' : 'text-error-600'}">
          {message.text}
        </span>
      {/if}
    </div>
  </Card>
</div>
