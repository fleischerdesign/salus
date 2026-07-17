<script lang="ts">
  import { liveQuery } from 'dexie';
  import { db } from '$lib/db/database';
  import type { FoodItem } from '$lib/db/types';
  import PageHeader from '$components/ui/PageHeader.svelte';
  import Card from '$components/ui/Card.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import Input from '$components/ui/Input.svelte';
  import Chip from '$components/ui/Chip.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import { createFoodItem } from '$lib/mutations/food-item';

  let loading = $state(true);
  let foodItems = $state<FoodItem[]>([]);
  let search = $state('');
  let createOpen = $state(false);
  let saving = $state(false);

  let newName = $state('');
  let newBrand = $state('');
  let newCalories = $state(0);
  let newProtein = $state(0);
  let newCarbs = $state(0);
  let newFat = $state(0);
  let newServingSize = $state(100);
  let newServingUnit = $state('g');

  $effect(() => {
    const sub = liveQuery(() =>
      db.food_item.where('deleted_at').equals('').or('deleted_at').equals(null as any).toArray()
    ).subscribe((v) => { foodItems = v; loading = false; });
    return () => sub.unsubscribe();
  });

  const results = $derived(
    search.trim()
      ? foodItems.filter((f) => f.name.toLowerCase().includes(search.toLowerCase())).slice(0, 20)
      : []
  );

  const frequentItems = $derived(foodItems.slice(0, 10));

  const canCreate = $derived(newName.trim().length > 0);

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
  <PageHeader
    title="Food Database"
    subtitle="Search and manage food items"
    icon="search"
    iconColor="#f59e0b"
  >
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <button
          type="button"
          class="duration-micro flex h-full items-center justify-center gap-2 bg-primary-500 px-6 text-sm font-semibold whitespace-nowrap text-white hover:bg-primary-600"
          onclick={() => (createOpen = true)}
        >
          <Icon name="add" class="text-base" /><span>New Item</span>
        </button>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
  {:else}
    <div class="max-w-xl">
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
                  <div class="text-xs text-surface-400 mt-0.5">
                    {item.serving_size}{item.serving_unit} · {item.calories_per_serving} kcal · {item.protein_g}P · {item.carbs_g}C · {item.fat_g}F
                  </div>
                </div>
                {#if item.is_verified}
                  <span class="flex-shrink-0 rounded-full bg-success-50 px-2 py-0.5 text-[10px] font-medium text-success-600">Verified</span>
                {:else if item.user_id}
                  <span class="flex-shrink-0 rounded-full bg-surface-100 px-2 py-0.5 text-[10px] font-medium text-surface-500">Custom</span>
                {/if}
              </div>
            {/each}
          </div>
        </Card>
      {:else}
        <p class="text-sm text-surface-400 text-center py-8">No results found. Create a new food item.</p>
      {/if}
    {:else if frequentItems.length > 0}
      <div>
        <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-surface-400">All Items</h3>
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
