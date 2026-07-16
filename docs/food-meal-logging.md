# Food / Meal Logging

## Overview
Detailliertes Ernährungstagebuch — über die existierenden Makro-Metriken (kcal, protein, carbs, fat) hinaus.
Mahlzeiten, Lebensmittel-DB, Favoriten, Barcode-Scan.

## Data Model

### food_item
(Lokale Lebensmittel-Datenbank, seeded mit Basis-Lebensmitteln)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| name | str | "Haferflocken" |
| brand | str? | "Alnatura" |
| barcode | str? | EAN/UPC |
| serving_size | float | 100 (g) |
| serving_unit | str | "g" |
| calories_per_serving | float | kcal |
| protein_g | float | |
| carbs_g | float | |
| fat_g | float | |
| fiber_g | float? | |
| sugar_g | float? | |
| saturated_fat_g | float? | |
| sodium_mg | float? | |
| is_verified | bool | User-created vs. verified |
| created_by | UUID? | User ID (null = system) |
| source | str? | "openfoodfacts" / "manual" |

### meal
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| date | date | |
| meal_type | enum | breakfast / lunch / dinner / snack / other |
| name | str? | "Porridge mit Banane" |
| notes | str? | |
| created_at | datetime | |

### meal_item
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| meal_id | UUID | FK → meal |
| food_item_id | UUID | FK → food_item |
| servings | float | 1.5 (Portionen) |
| amount_g | float? | Tatsächliche Gramm |

### recipe
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK |
| name | str | "Protein-Pancakes" |
| description | str? | |
| instructions | str? | Markdown |
| servings | int | 4 Portionen |
| prep_time_min | int? | |
| cook_time_min | int? | |
| is_favorite | bool | |
| created_at | datetime | |

### recipe_ingredient
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| recipe_id | UUID | FK → recipe |
| food_item_id | UUID | FK → food_item |
| amount_g | float | Gramm |
| notes | str? | "gehackt" |

### meal_photo
(Optional — Bilder von Mahlzeiten)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| meal_id | UUID | FK → meal |
| file_path | str | Lokaler Pfad |
| created_at | datetime | |

## API Endpoints

### Food Items
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/food/items/search | Search (q, barcode) |
| POST | /api/v1/food/items | Create custom item |
| GET | /api/v1/food/items/{id} | Get details |
| GET | /api/v1/food/items/barcode/{code} | Lookup by barcode |

### Meals
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/meals | List (date range filter) |
| POST | /api/v1/meals | Create meal with items |
| GET | /api/v1/meals/{id} | Get meal |
| PUT | /api/v1/meals/{id} | Update |
| DELETE | /api/v1/meals/{id} | Delete |
| GET | /api/v1/meals/today | Today's meals |
| GET | /api/v1/meals/summary | Macro totals (date range) |

### Recipes
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/recipes | List recipes |
| POST | /api/v1/recipes | Create recipe |
| GET | /api/v1/recipes/{id} | Get recipe |
| PUT | /api/v1/recipes/{id} | Update |
| DELETE | /api/v1/recipes/{id} | Delete |
| POST | /api/v1/recipes/{id}/cook | Log as meal (creates meal from recipe) |

### Favorites & Frequent
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/food/frequent | Most-used items |
| GET | /api/v1/food/recent | Recently used |

## Frontend

- **FoodSearch** — Suchleiste mit Autocomplete (Food-DB + eigene Items)
- **BarcodeScanner** — Kamera-Barcode-Scan (ZXing/QuaggaJS library)
- **MealForm** — Mahlzeit-Typ wählen, Items hinzufügen, Portionen anpassen
- **MealList** — Tagesübersicht mit Makro-Summe pro Mahlzeit
- **RecipeBook** — Rezept-Liste mit Bildern, Favoriten-Filter
- **RecipeDetail** — Zutaten, Anleitung, "Kochen"-Button
- **NutritionSummary** — Tages-/Wochenübersicht: Kalorien, Makros, Mikros
- **CalorieTarget** — TDEE-Rechner + Ziel-Konfiguration (Bulk/Cut/Maintenance)
- **FoodTimeline** — Chronologische Mahlzeiten-Ansicht (wie MedicationTimeline)

## Integration Points
- **OpenFoodFacts API** → Barcode-Lookup und Lebensmittel-DB-Befüllung
- **Metrics** → Makros als MetricTypes loggen (existiert bereits)
- **Analytics** → Kalorien-Trend, Makro-Verteilung, Mikro-Defizite erkennen
- **Goals** → "180g Protein pro Tag"
- **Workout Autoregulation** → Kalorienbilanz für Recovery-Score
- **Insights/AI Coach** → Ernährungs-Coaching

## Open Questions
- OpenFoodFacts: Client-seitig (CORS) oder Server-seitig (Proxy)? Rate-Limits beachten.
- Barcode-Scan: Browser-API (`BarcodeDetector`) oder JS-Library? `BarcodeDetector` ist Chrome-only.
- Soll es Meal-Photos geben? Wenn ja: Lokal in IndexedDB oder Server-Upload?
- Wie granular soll die Food-DB sein? Seed mit Top-1000 Lebensmitteln oder nur user-generated?

## Ergänzungen von Philipp
Hier auch wieder ein Hinweis darauf, dass wir unser Metrik System als Herzstück nicht vergessen dürfen.
OpenFoodFacts: Wir könnten dem einzelnen User ja die Möglichkeit geben, einen eigenen API Key zu hinterlegen, aber eben auch die Möglichkeit bieten, den Server Proxy dafür zu nutzen.
Barcode-Scan: Gute Frage, ich denke es ist wichtig, dass wir alle Browser abdecken.
Meal Photos: Ja! Sowohl lokal als auch auf dem Server.. Wir haben hier eine Offline First Architektur, dessen Daten aber auch auf dem Server verfügbar sind, falls dir das noch nicht aufgefallen ist.
Granularität: Das verstehe ich nicht ganz.. Nutzen wir nicht eine API? Speichern wir die Lebensmittel selbst auf der Salus instanz? 