export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface FoodItem {
  id: string;
  name: string;
  brand?: string;
  category: 'Protein' | 'Kohlenhydrate' | 'Fette' | 'Gemüse und Obst' | 'Snacks und Shakes';
  per100g: {
    kcal: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sugar?: number;
  };
  defaultServingG: number;
  servingName: string;
}

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
  icon: string;
  items: LoggedFoodItem[];
}

export interface RecipeIngredient {
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
