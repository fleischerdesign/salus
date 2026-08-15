<script lang="ts">
  import { db } from '$lib/db/database';

  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import { goto } from '$app/navigation';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Chip from '$components/ui/Chip.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Modal from '$components/ui/Modal.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import FormField from '$components/forms/FormField.svelte';
  import { createFoodItem, updateFoodItem, deleteFoodItem } from '$lib/mutations/food-item';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { api } from '$lib/api/client';
  import type { FoodItem } from '$lib/db/types';

  let search = $state('');
  let createOpen = $state(false);
  let saving = $state(false);
  let barcode = $state('');
  let lookingUp = $state(false);
  let lookupMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);
  let editingItem = $state<FoodItem | null>(null);
  let deleteTarget = $state<FoodItem | null>(null);

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

  function openCreate() {
    editingItem = null;
    newName = '';
    newBrand = '';
    newCalories = 0;
    newProtein = 0;
    newCarbs = 0;
    newFat = 0;
    newServingSize = 100;
    newServingUnit = 'g';
    createOpen = true;
  }

  function openEdit(item: FoodItem) {
    editingItem = item;
    newName = item.name;
    newBrand = item.brand ?? '';
    newCalories = item.calories_per_serving;
    newProtein = item.protein_g;
    newCarbs = item.carbs_g;
    newFat = item.fat_g;
    newServingSize = item.serving_size;
    newServingUnit = item.serving_unit;
    createOpen = true;
  }

  async function handleCreate() {
    if (!canCreate) return;
    saving = true;
    try {
      const payload = {
        name: newName.trim(),
        brand: newBrand.trim() || undefined,
        calories_per_serving: newCalories,
        protein_g: newProtein,
        carbs_g: newCarbs,
        fat_g: newFat,
        serving_size: newServingSize,
        serving_unit: newServingUnit
      };
      if (editingItem) {
        await updateFoodItem(editingItem.id, payload);
      } else {
        await createFoodItem(payload);
      }
      createOpen = false;
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await deleteFoodItem(deleteTarget.id);
    deleteTarget = null;
  }
</script>

<svelte:head><title>Salus — Food Database</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Food Database" subtitle="Search and manage food items" icon="search">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction variant="secondary" icon="restaurant" onclick={() => goto('/meals')}
          >Meals</PageHeaderAction
        >
        <PageHeaderAction variant="secondary" icon="menu-book" onclick={() => goto('/recipes')}
          >Recipes</PageHeaderAction
        >
        <PageHeaderAction icon="add" onclick={openCreate}>New Item</PageHeaderAction>
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
              <div class="flex items-start justify-between gap-3 px-4 py-3">
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
                <div class="flex flex-shrink-0 items-center gap-2">
                  {#if item.is_verified}
                    <span
                      class="rounded-full bg-success-50 px-2 py-0.5 text-[10px] font-medium text-success-600"
                      >Verified</span
                    >
                  {:else if item.user_id}
                    <span
                      class="rounded-full bg-surface-100 px-2 py-0.5 text-[10px] font-medium text-surface-500"
                      >Custom</span
                    >
                  {/if}
                  {#if item.user_id}
                    <button
                      type="button"
                      class="flex h-7 w-7 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-primary-600"
                      aria-label="Edit {item.name}"
                      onclick={() => openEdit(item)}
                    >
                      <Icon name="edit" size="sm" />
                    </button>
                    <button
                      type="button"
                      class="flex h-7 w-7 items-center justify-center rounded text-surface-400 hover:bg-surface-100 hover:text-error-500"
                      aria-label="Delete {item.name}"
                      onclick={() => (deleteTarget = item)}
                    >
                      <Icon name="delete" size="sm" />
                    </button>
                  {/if}
                </div>
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

  <Modal
    open={createOpen}
    onclose={() => (createOpen = false)}
    title={editingItem ? 'Edit Food Item' : 'New Food Item'}
    size="md"
  >
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
          {saving ? 'Saving...' : editingItem ? 'Save' : 'Create'}
        </Btn>
      </div>
    </div>
  </Modal>

  <ConfirmDialog
    open={deleteTarget !== null}
    title="Delete Food Item"
    variant="danger"
    message={deleteTarget
      ? `Delete "${deleteTarget.name}"? Meals using it will show 0 kcal for it.`
      : ''}
    confirmLabel="Delete"
    onconfirm={handleDelete}
    oncancel={() => (deleteTarget = null)}
  />
</div>
