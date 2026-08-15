<script lang="ts">
  import { db } from '$lib/db/database';

  import PageHeader from '$components/ui/PageHeader.svelte';
  import PageHeaderAction from '$components/ui/PageHeaderAction.svelte';
  import Card from '$components/ui/Card.svelte';
  import Input from '$components/ui/Input.svelte';
  import Chip from '$components/ui/Chip.svelte';
  import Spinner from '$components/ui/Spinner.svelte';
  import Btn from '$components/ui/Btn.svelte';
  import Icon from '$components/ui/Icon.svelte';
  import ConfirmDialog from '$components/ui/ConfirmDialog.svelte';
  import BarcodeScanner from '$components/food/BarcodeScanner.svelte';
  import BarcodeNotFound from '$components/food/BarcodeNotFound.svelte';
  import FoodDetailModal from '$components/food/FoodDetailModal.svelte';
  import FoodFormModal from '$components/food/FoodFormModal.svelte';
  import PortionPickerModal from '$components/food/PortionPickerModal.svelte';
  import { deleteFoodItem } from '$lib/mutations/food-item';
  import { useQuery } from '$lib/db/use-query.svelte';
  import { lookupBarcode } from '$lib/food/barcode';
  import { goto } from '$app/navigation';
  import type { FoodItem } from '$lib/db/types';

  let search = $state('');
  let lookupMessage = $state<{ type: 'success'; text: string } | null>(null);
  let notFoundBarcode = $state<string | null>(null);
  let createBarcode = $state<string | null>(null);
  let deleteTarget = $state<FoodItem | null>(null);
  let deleteOpen = $state(false);
  let selectedFood = $state<FoodItem | null>(null);
  let formOpen = $state(false);
  let editingFood = $state<FoodItem | null>(null);
  let addToMealFood = $state<FoodItem | null>(null);

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

  async function handleBarcodeLookup(code: string) {
    const value = code.trim();
    if (!value) return;
    lookupMessage = null;
    notFoundBarcode = null;
    try {
      const found = await lookupBarcode(value);
      if (found) {
        lookupMessage = { type: 'success', text: `Found: ${found.name}` };
        search = found.name;
      } else {
        notFoundBarcode = value;
      }
    } catch {
      notFoundBarcode = value;
    }
  }

  function openCreateFromScan() {
    createBarcode = notFoundBarcode;
    notFoundBarcode = null;
    openCreate();
  }

  function openCreate() {
    editingFood = null;
    formOpen = true;
  }

  function openEdit(food: FoodItem) {
    editingFood = food;
    formOpen = true;
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    await deleteFoodItem(deleteTarget.id);
    deleteTarget = null;
    selectedFood = null;
    deleteOpen = false;
  }

  function addToMeal(food: FoodItem) {
    addToMealFood = food;
  }

  function handleAddToMeal(food: FoodItem, servings: number) {
    addToMealFood = null;
    selectedFood = null;
    goto(`/meals?add=${encodeURIComponent(food.id ?? '')}&servings=${servings}`);
  }
</script>

<svelte:head><title>Salus — Food Database</title></svelte:head>

<div class="space-y-6">
  <PageHeader title="Food Database" subtitle="Search and manage food items" icon="search">
    {#snippet actions()}
      <div class="flex h-full items-stretch">
        <PageHeaderAction icon="add" onclick={openCreate}>New Item</PageHeaderAction>
      </div>
    {/snippet}
  </PageHeader>

  {#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
  {:else}
    <div class="max-w-xl space-y-3">
      <BarcodeScanner onScan={handleBarcodeLookup} variant="primary" />

      {#if lookupMessage}
        <p class="text-sm text-success-600">{lookupMessage.text}</p>
      {/if}

      {#if notFoundBarcode}
        <BarcodeNotFound
          barcode={notFoundBarcode}
          onCreate={openCreateFromScan}
          onDismiss={() => (notFoundBarcode = null)}
        />
      {/if}

      <Input name="search_food" placeholder="Search food items..." bind:value={search} />
    </div>

    {#if search.trim()}
      {#if results.length > 0}
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {#each results as item (item.id)}
            <button type="button" onclick={() => (selectedFood = item)} class="text-left">
              <Card padding={false} hoverable class="h-full">
                <div class="flex items-start justify-between gap-3 p-4">
                  <div class="min-w-0">
                    <div class="truncate text-sm font-semibold text-surface-800">
                      {item.name}
                      {#if item.brand}
                        <span class="font-normal text-surface-400">({item.brand})</span>
                      {/if}
                    </div>
                    <div class="mt-1 text-xs text-surface-400">
                      {item.serving_size}{item.serving_unit} · {Math.round(
                        item.calories_per_serving
                      )} kcal
                    </div>
                    <div class="mt-1.5 flex flex-wrap gap-x-3 text-xs">
                      <span class="text-primary-600">P {Math.round(item.protein_g)}g</span>
                      <span class="text-warning-600">C {Math.round(item.carbs_g)}g</span>
                      <span class="text-error-500">F {Math.round(item.fat_g)}g</span>
                    </div>
                  </div>
                  <div class="flex flex-shrink-0 flex-col items-end gap-1.5">
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
                    <Icon name="chevron-right" size="sm" class="text-surface-300" />
                  </div>
                </div>
              </Card>
            </button>
          {/each}
        </div>
      {:else}
        <Card>
          <div class="flex flex-col items-center gap-2 py-8 text-center">
            <p class="text-sm font-medium text-surface-700">No results for "{search}"</p>
            <Btn variant="secondary" size="sm" onclick={openCreate}>
              <Icon name="add" size="sm" />
              Create food item
            </Btn>
          </div>
        </Card>
      {/if}
    {:else if frequentItems.length > 0}
      <div>
        <h2 class="mb-3 text-xs font-semibold tracking-wider text-surface-400 uppercase">
          All Items
        </h2>
        <div class="flex flex-wrap gap-2">
          {#each frequentItems as item (item.id)}
            <button type="button" onclick={() => (selectedFood = item)}>
              <Chip variant="neutral">{item.name}</Chip>
            </button>
          {/each}
        </div>
      </div>
    {/if}
  {/if}

  <FoodFormModal
    open={formOpen}
    food={editingFood}
    initialBarcode={createBarcode}
    onClose={() => {
      formOpen = false;
      createBarcode = null;
    }}
  />

  <FoodDetailModal
    food={selectedFood}
    onAddToMeal={addToMeal}
    onEdit={(food) => {
      selectedFood = null;
      openEdit(food);
    }}
    onDelete={(food) => {
      deleteTarget = food;
      selectedFood = null;
      deleteOpen = true;
    }}
    onClose={() => (selectedFood = null)}
  />

  <PortionPickerModal
    food={addToMealFood}
    onAdd={handleAddToMeal}
    onClose={() => (addToMealFood = null)}
  />

  <ConfirmDialog
    bind:open={deleteOpen}
    title="Delete Food Item"
    variant="danger"
    message={deleteTarget
      ? `Delete "${deleteTarget.name}"? Items in existing meals are unaffected.`
      : ''}
    confirmLabel="Delete"
    onconfirm={handleDelete}
  />
</div>
