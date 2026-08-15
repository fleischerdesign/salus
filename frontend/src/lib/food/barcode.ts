import { db } from '$lib/db/database';
import { api } from '$lib/api/client';
import { uuid7 } from '$lib/db/uuid';
import { localMode } from '$lib/db/local-mode.svelte';
import type { FoodItem } from '$lib/db/types';

const DIRECT_API_KEY = 'salus_food_direct_api';
const OFF_KEY_KEY = 'salus_food_off_key';
const OFF_API = 'https://world.openfoodfacts.org/api/v2/product/{barcode}.json';
const OFF_USER_AGENT = 'SalusHealth/0.1 (self-hosted health tracker)';

function directOffEnabled(): boolean {
  return typeof localStorage !== 'undefined' && localStorage.getItem(DIRECT_API_KEY) === 'true';
}

export function setDirectOffEnabled(enabled: boolean): void {
  if (typeof localStorage === 'undefined') return;
  if (enabled) localStorage.setItem(DIRECT_API_KEY, 'true');
  else localStorage.removeItem(DIRECT_API_KEY);
}

export function offApiKey(): string {
  if (typeof localStorage === 'undefined') return '';
  return localStorage.getItem(OFF_KEY_KEY) ?? '';
}

export function setOffApiKey(key: string): void {
  if (typeof localStorage === 'undefined') return;
  if (key) localStorage.setItem(OFF_KEY_KEY, key);
  else localStorage.removeItem(OFF_KEY_KEY);
}

function toFoodItem(found: Partial<FoodItem>, barcode: string): FoodItem {
  const now = new Date().toISOString();
  return {
    id: found.id ?? uuid7(),
    name: found.name ?? `Produkt ${barcode}`,
    brand: found.brand ?? null,
    barcode: found.barcode ?? barcode,
    serving_size: found.serving_size ?? 100,
    serving_unit: found.serving_unit ?? 'g',
    calories_per_serving: found.calories_per_serving ?? 0,
    protein_g: found.protein_g ?? 0,
    carbs_g: found.carbs_g ?? 0,
    fat_g: found.fat_g ?? 0,
    fiber_g: found.fiber_g ?? null,
    sugar_g: found.sugar_g ?? null,
    saturated_fat_g: found.saturated_fat_g ?? null,
    sodium_mg: found.sodium_mg ?? null,
    is_verified: found.is_verified ?? true,
    user_id: found.user_id ?? null,
    source: found.source ?? 'openfoodfacts',
    created_at: found.created_at ?? now,
    updated_at: null,
    deleted_at: null
  };
}

async function lookupOffDirect(code: string): Promise<FoodItem | null> {
  try {
    const key = offApiKey();
    const url = key
      ? `${OFF_API.replace('{barcode}', encodeURIComponent(code))}?key=${encodeURIComponent(key)}`
      : OFF_API.replace('{barcode}', encodeURIComponent(code));
    const resp = await fetch(url, { headers: { 'User-Agent': OFF_USER_AGENT } });
    if (!resp.ok) return null;
    const payload = await resp.json();
    if (payload.status !== 1) return null;
    const product = payload.product ?? {};
    const n = product.nutriments ?? {};
    return toFoodItem(
      {
        id: uuid7(),
        name: product.product_name || product.product_name_en || null,
        brand: product.brands ?? null,
        serving_size: 100,
        serving_unit: 'g',
        calories_per_serving: n['energy-kcal_100g'] ?? 0,
        protein_g: n['proteins_100g'] ?? 0,
        carbs_g: n['carbohydrates_100g'] ?? 0,
        fat_g: n['fat_100g'] ?? 0,
        fiber_g: n['fiber_100g'] ?? null,
        sugar_g: n['sugars_100g'] ?? null,
        saturated_fat_g: n['saturated-fat_100g'] ?? null,
        sodium_mg: n['sodium_100g'] ?? null,
        is_verified: true,
        user_id: null,
        source: 'openfoodfacts'
      },
      code
    );
  } catch {
    return null;
  }
}

/**
 * Resolve a barcode to a food item: local Dexie, then the server proxy, then
 * (in local mode) the OpenFoodFacts API directly. Results are cached locally.
 */
export async function lookupBarcode(code: string): Promise<FoodItem | null> {
  const local = await db.food_item.where('barcode').equals(code).first();
  if (local && !local.deleted_at) return local;

  if (!localMode.active) {
    const res = await api.GET('/api/v1/food/items/barcode/{barcode}', {
      params: { path: { barcode: code } }
    });
    const found = res.data as Partial<FoodItem> | null;
    if (found?.id && found.name) {
      const item = toFoodItem(found, code);
      await db.food_item.put(item);
      return item;
    }
    return null;
  }

  if (directOffEnabled()) {
    const item = await lookupOffDirect(code);
    if (item) {
      await db.food_item.put(item);
      return item;
    }
  }
  return null;
}
