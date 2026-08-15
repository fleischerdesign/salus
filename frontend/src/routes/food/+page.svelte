<script lang="ts">
  import { db } from '$lib/db/database';

  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Chip from '$components/ui/Chip.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import { createFoodItem } from '$lib/mutations/food-item';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { api } from '$lib/api/client';
  import type { FoodItem } from '$lib/db/types';

  let search = $state('');
  let createOpen = $state(false);
  let saving = $state(false);
  let barcode = $state('');
  let lookingUp = $state(false);
  let lookupMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);

  let newName = $state('');
  let newBrand = $state('');
  let newCalories = $state(0);
  let newProtein = $state(0);
  let newCarbs = $state(0);
  let newFat = $state(0);
  let newServingSize = $state(100);
  let newServingUnit = $state('g');

  const foodItemsQuery = useQuery(() => db.notDeleted(db.food_item).toArray());
  const foodItems = $derived(foodItemsQuery.value);
  const loading = $derived(foodItemsQuery.loading);

  const results = $derived(
    search.trim()
      ? (foodItems ?? [])
          .filter((f) => f.name.toLowerCase().includes(search.toLowerCase()))
          .slice(0, 20)
      : []
  );

  const frequentItems = $derived((foodItems ?? []).slice(0, 10));

  const canCreate = $derived(newName.trim().length > 0);

  async function handleBarcodeLookup() {
    const code = barcode.trim();
    if (!code) return;
    lookingUp = true;
    lookupMessage = null;
    try {
      const local = await db.food_item.where('barcode').equals(code).first();
      if (local && !local.deleted_at) {
        lookupMessage = { type: 'success', text: `Already in database: ${local.name}` };
        search = local.name;
        return;
      }
      const res = await api.GET('/api/v1/food/items/barcode/{barcode}', {
        params: { path: { barcode: code } }
      });
      const found = res.data as Partial<FoodItem> | null;
      if (found?.id && found.name) {
        await db.food_item.put({
          ...found,
          serving_size: found.serving_size ?? 100,
          serving_unit: found.serving_unit ?? 'g',
          calories_per_serving: found.calories_per_serving ?? 0,
          protein_g: found.protein_g ?? 0,
          carbs_g: found.carbs_g ?? 0,
          fat_g: found.fat_g ?? 0,
          user_id: found.user_id ?? null,
          is_verified: found.is_verified ?? true,
          source: found.source ?? 'openfoodfacts',
          updated_at: null,
          deleted_at: null
        } as FoodItem);
        lookupMessage = { type: 'success', text: `Added: ${found.name}` };
        search = found.name;
      } else {
        lookupMessage = { type: 'error', text: 'Barcode not found. Create it manually.' };
      }
    } catch {
      lookupMessage = { type: 'error', text: 'Lookup failed — are you online?' };
    } finally {
      lookingUp = false;
    }
  }

  async function handleCreate() {
    if (!canCreate) return;
    saving = true;
    try {
      await createFoodItem({
        name: newName.trim(),
        brand: newBrand.trim() || undefined,
        calories_per_serving: newCalories,
        protein_g: newProtein,
        carbs_g: newCarbs,
        fat_g: newFat,
        serving_size: newServingSize,
        serving_unit: newServingUnit
      });
      createOpen = false;
      newName = '';
      newBrand = '';
      newCalories = 0;
      newProtein = 0;
      newCarbs = 0;
      newFat = 0;
      newServingSize = 100;
      newServingUnit = 'g';
    } finally {
      saving = false;
    }
  }
</script>

<svelte:head><title>Salus — Food Database</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Food Database" subtitle="Search and manage food items" icon="search">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction icon="add" onclick={() => (createOpen = true)}>New Item</PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
  {:else}
    <div class="max-w-xl space-y-3">
      <form
        class="flex items-end gap-2"
        onsubmit={(e) => {
          e.preventDefault();
          handleBarcodeLookup();
        }}
      >
        <div class="flex-1">
          <Input name="barcode" placeholder="Barcode (EAN/UPC)…" bind:value={barcode} />
        </div>
        <Btn variant="secondary" onclick={handleBarcodeLookup} loading={lookingUp}>Lookup</Btn>
      </form>
      {#if lookupMessage}
        <p
          class="text-sm {lookupMessage.type === 'success' ? 'text-success-600' : 'text-error-600'}"
        >
          {lookupMessage.text}
        </p>
      {/if}
      <Input name="search_food" placeholder="Search food items..." bind:value={search} />
    </div>

    {#if search.trim()}
      {#if results.length > 0}
        <Card>
          <div class="divide-y divide-surface-100">
            {#each results as item (item.id)}
              <div class="flex items-start justify-between px-4 py-3">
                <div>
                  <div class="text-sm font-medium text-surface-800">
                    {item.name}
                    {#if item.brand}
                      <span class="text-surface-400">({item.brand})</span>
                    {/if}
                  </div>
                  <div class="mt-0.5 text-xs text-surface-400">
                    {item.serving_size}{item.serving_unit} · {item.calories_per_serving} kcal · {item.protein_g}P
                    · {item.carbs_g}C · {item.fat_g}F
                  </div>
                </div>
                {#if item.is_verified}
                  <span
                    class="flex-shrink-0 rounded-full bg-success-50 px-2 py-0.5 text-[10px] font-medium text-success-600"
                    >Verified</span
                  >
                {:else if item.user_id}
                  <span
                    class="flex-shrink-0 rounded-full bg-surface-100 px-2 py-0.5 text-[10px] font-medium text-surface-500"
                    >Custom</span
                  >
                {/if}
              </div>
            {/each}
          </div>
        </Card>
      {:else}
        <p class="py-8 text-center text-sm text-surface-400">
          No results found. Create a new food item.
        </p>
      {/if}
    {:else if frequentItems.length > 0}
      <div>
        <h2 class="mb-3 text-xs font-semibold tracking-wider text-surface-400 uppercase">
          All Items
        </h2>
        <div class="flex flex-wrap gap-2">
          {#each frequentItems as item (item.id)}
            <Chip variant="neutral">{item.name}</Chip>
          {/each}
        </div>
      </div>
    {/if}
  {/if}

  <Modal open={createOpen} onclose={() => (createOpen = false)} title="New Food Item" size="md">
    <div class="flex flex-col gap-4">
      <FormField label="Name" required>
        <Input name="food_name" placeholder="e.g. Haferflocken" bind:value={newName} />
      </FormField>
      <FormField label="Brand">
        <Input name="brand" placeholder="e.g. Alnatura" bind:value={newBrand} />
      </FormField>
      <div class="grid grid-cols-2 gap-4">
        <FormField label="Serving Size">
          <Input name="serving_size" type="number" bind:value={newServingSize} min={1} />
        </FormField>
        <FormField label="Unit">
          <Input name="serving_unit" placeholder="g" bind:value={newServingUnit} />
        </FormField>
      </div>
      <div class="grid grid-cols-2 gap-4">
        <FormField label="Calories (per serving)">
          <Input name="calories" type="number" bind:value={newCalories} step={0.1} />
        </FormField>
        <FormField label="Protein (g)">
          <Input name="protein" type="number" bind:value={newProtein} step={0.1} />
        </FormField>
        <FormField label="Carbs (g)">
          <Input name="carbs" type="number" bind:value={newCarbs} step={0.1} />
        </FormField>
        <FormField label="Fat (g)">
          <Input name="fat" type="number" bind:value={newFat} step={0.1} />
        </FormField>
      </div>
      <div class="flex justify-end gap-3 pt-2">
        <Btn variant="ghost" onclick={() => (createOpen = false)}>Cancel</Btn>
        <Btn variant="primary" onclick={handleCreate} disabled={!canCreate || saving}>
          {saving ? 'Saving...' : 'Create'}
        </Btn>
      </div>
    </div>
  </Modal>
</div>
