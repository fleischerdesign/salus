export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface FoodItem {
  id: string;
  name: string;
  brand?: string;
  category?: string;
  source?: string;
  barcode?: string;
  per100g?: {
    kcal: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sugar?: number;
    sodium?: number;
  };
  defaultServingG?: number;
  servingName?: string;
  servingSizeG?: number;
  kcalPer100g?: number;
  proteinPer100g?: number;
  carbsPer100g?: number;
  fatPer100g?: number;
  fiberPer100g?: number;
  sugarPer100g?: number;
  sodiumPer100g?: number;
  verified?: boolean;
}

export type FoodItemData = FoodItem;

export interface LoggedFoodItem {
  id: string;
  name: string;
  amountG: number;
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
}

export interface MealSlotData {
  id: string;
  type: MealType;
  title: string;
  time: string;
  icon?: string;
  items: LoggedFoodItem[];
}

export interface RecipeIngredient {
  id?: string;
  foodId?: string;
  name: string;
  amount: number;
  unit: string;
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface RecipeData {
  id: string;
  title: string;
  category: string;
  prepTime: string;
  basePortions: number;
  currentPortions: number;
  ingredients: RecipeIngredient[];
  instructions: string[];
  rating: string;
  kcalPerPortion: number;
  proteinPerPortion: number;
  carbsPerPortion: number;
  fatPerPortion: number;
}
