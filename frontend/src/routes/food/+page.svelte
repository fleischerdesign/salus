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
  import { lookupBarcode, setDirectOffEnabled, setOffApiKey, offApiKey } from '$lib/food/barcode';
  import { localMode } from '$lib/db/local-mode.svelte';
  import type { FoodItem } from '$lib/db/types';

  let search = $state('');
  let createOpen = $state(false);
  let saving = $state(false);
  let barcode = $state('');
  let lookingUp = $state(false);
  let lookupMessage = $state<{ type: 'success' | 'error'; text: string } | null>(null);
  let editingItem = $state<FoodItem | null>(null);
  let deleteTarget = $state<FoodItem | null>(null);
  let directOff = $state(localStorage.getItem('salus_food_direct_api') === 'true');
  let offKey = $state(offApiKey());
  let scanning = $state(false);
  let cameraEl = $state<HTMLVideoElement | null>(null);
  let scanner = $state<{ stop: () => void } | null>(null);
  let scanUnsupported = $state(typeof window !== 'undefined' && !('BarcodeDetector' in window));

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

  async function handleBarcodeLookup(code?: string) {
    const value = (code ?? barcode).trim();
    if (!value) return;
    lookingUp = true;
    lookupMessage = null;
    try {
      const found = await lookupBarcode(value);
      if (found) {
        lookupMessage = { type: 'success', text: `Found: ${found.name}` };
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

  function toggleDirectOff(enabled: boolean) {
    directOff = enabled;
    setDirectOffEnabled(enabled);
  }

  function handleOffKey(value: string) {
    offKey = value;
    setOffApiKey(value.trim());
  }

  function cleanupScanner() {
    scanner?.stop();
    scanner = null;
    if (cameraEl) cameraEl.srcObject = null;
    scanning = false;
  }

  async function startScanner() {
    if (scanning) {
      cleanupScanner();
      return;
    }
    scanning = true;
    lookupMessage = null;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      if (cameraEl) cameraEl.srcObject = stream;
      await cameraEl?.play();

      const Detector = (
        window as unknown as {
          BarcodeDetector: new (o: unknown) => {
            detect: (v: HTMLVideoElement) => Promise<Array<{ rawValue: string }>>;
          };
        }
      ).BarcodeDetector;
      const detector = new Detector({ formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128'] });

      const interval = window.setInterval(async () => {
        try {
          const codes = await detector.detect(cameraEl!);
          if (codes.length > 0) {
            const raw = codes[0].rawValue;
            window.clearInterval(interval);
            cleanupScanner();
            barcode = raw;
            await handleBarcodeLookup(raw);
          }
        } catch {
          /* frame skipped */
        }
      }, 200);

      scanner = {
        stop() {
          window.clearInterval(interval);
          stream.getTracks().forEach((t) => t.stop());
        }
      };
    } catch {
      scanning = false;
      lookupMessage = { type: 'error', text: 'Camera unavailable — type the barcode instead.' };
    }
  }

  $effect(() => {
    if (!scanning) return;
    return () => cleanupScanner();
  });

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
        {#if !scanUnsupported}
          <Btn
            variant="secondary"
            onclick={startScanner}
            class={scanning ? 'border-primary-500 text-primary-600' : ''}
          >
            <Icon name={scanning ? 'close' : 'camera-alt'} size="sm" />
            {scanning ? 'Stop' : 'Scan'}
          </Btn>
        {/if}
        <Btn variant="secondary" onclick={() => handleBarcodeLookup()} loading={lookingUp}
          >Lookup</Btn
        >
      </form>

      {#if scanning}
        <div class="overflow-hidden rounded-lg border border-primary-300">
          <video bind:this={cameraEl} class="bg-surface-950 max-h-64 w-full" muted playsinline
          ></video>
        </div>
        {#if scanUnsupported}
          <p class="text-xs text-surface-400">
            Camera scanning needs a Chromium-based browser. Type the barcode instead.
          </p>
        {/if}
      {/if}

      {#if lookupMessage}
        <p
          class="text-sm {lookupMessage.type === 'success' ? 'text-success-600' : 'text-error-600'}"
        >
          {lookupMessage.text}
        </p>
      {/if}

      {#if localMode.active}
        <div class="rounded-lg border border-surface-200 p-3">
          <label class="flex items-center justify-between text-sm text-surface-700">
            <span>Direct OpenFoodFacts lookup (offline)</span>
            <input
              type="checkbox"
              checked={directOff}
              onchange={(e) => toggleDirectOff(e.currentTarget.checked)}
            />
          </label>
          {#if directOff}
            <input
              type="text"
              class="mt-2 h-9 w-full rounded-md border border-surface-300 bg-surface-50 px-3 text-sm text-surface-900 focus:border-primary-500 focus:outline-none"
              placeholder="Optional OFF API key"
              value={offKey}
              oninput={(e) => handleOffKey(e.currentTarget.value)}
            />
          {/if}
        </div>
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
