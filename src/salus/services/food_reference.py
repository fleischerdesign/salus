"""Seed data for the common-food database (system items, shared across users).

Values are per serving (serving_size=100 g) and kept deliberately small so the
bundle stays lean (ADR 012); larger datasets come from the barcode proxy cache
or an admin bulk import.
"""

COMMON_FOODS: list[dict] = [
    # ── Grains ──
    {"id": "food-oatmeal", "name": "Haferflocken", "serving_size": 100, "calories_per_serving": 389, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9, "fiber_g": 10.6, "sugar_g": 1.0},
    {"id": "food-rice-cooked", "name": "Reis (gekocht)", "serving_size": 100, "calories_per_serving": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3},
    {"id": "food-wholewheat-bread", "name": "Vollkornbrot", "serving_size": 100, "calories_per_serving": 247, "protein_g": 13.0, "carbs_g": 41.0, "fat_g": 3.4, "fiber_g": 7.0},
    {"id": "food-pasta-cooked", "name": "Pasta (gekocht)", "serving_size": 100, "calories_per_serving": 158, "protein_g": 5.8, "carbs_g": 31.0, "fat_g": 0.9},
    {"id": "food-quinoa-cooked", "name": "Quinoa (gekocht)", "serving_size": 100, "calories_per_serving": 120, "protein_g": 4.4, "carbs_g": 21.0, "fat_g": 1.9, "fiber_g": 2.8},
    {"id": "food-potato-cooked", "name": "Kartoffel (gekocht)", "serving_size": 100, "calories_per_serving": 87, "protein_g": 1.9, "carbs_g": 20.0, "fat_g": 0.1, "fiber_g": 1.8},
    {"id": "food-sweet-potato", "name": "Süßkartoffel", "serving_size": 100, "calories_per_serving": 86, "protein_g": 1.6, "carbs_g": 20.0, "fat_g": 0.1, "fiber_g": 3.0},
    # ── Protein ──
    {"id": "food-chicken-breast", "name": "Hähnchenbrust (gebraten)", "serving_size": 100, "calories_per_serving": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6},
    {"id": "food-ground-beef", "name": "Rinderhack (mager)", "serving_size": 100, "calories_per_serving": 250, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 15.0},
    {"id": "food-eggs", "name": "Eier", "serving_size": 100, "calories_per_serving": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0},
    {"id": "food-salmon", "name": "Lachs", "serving_size": 100, "calories_per_serving": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0},
    {"id": "food-tuna", "name": "Thunfisch", "serving_size": 100, "calories_per_serving": 132, "protein_g": 28.0, "carbs_g": 0.0, "fat_g": 1.3},
    {"id": "food-tofu", "name": "Tofu", "serving_size": 100, "calories_per_serving": 76, "protein_g": 8.0, "carbs_g": 1.9, "fat_g": 4.8},
    {"id": "food-greek-yogurt", "name": "Griechischer Joghurt", "serving_size": 100, "calories_per_serving": 59, "protein_g": 10.0, "carbs_g": 3.6, "fat_g": 0.4},
    {"id": "food-cottage-cheese", "name": "Hüttenkäse", "serving_size": 100, "calories_per_serving": 98, "protein_g": 11.0, "carbs_g": 3.4, "fat_g": 4.3},
    {"id": "food-lentils-cooked", "name": "Linsen (gekocht)", "serving_size": 100, "calories_per_serving": 116, "protein_g": 9.0, "carbs_g": 20.0, "fat_g": 0.4, "fiber_g": 7.9},
    {"id": "food-chickpeas-cooked", "name": "Kichererbsen (gekocht)", "serving_size": 100, "calories_per_serving": 164, "protein_g": 8.9, "carbs_g": 27.0, "fat_g": 2.6, "fiber_g": 7.6},
    # ── Dairy ──
    {"id": "food-milk-whole", "name": "Milch (3,5%)", "serving_size": 100, "calories_per_serving": 61, "protein_g": 3.2, "carbs_g": 4.8, "fat_g": 3.3},
    {"id": "food-milk-skim", "name": "Milch (fettarm)", "serving_size": 100, "calories_per_serving": 34, "protein_g": 3.4, "carbs_g": 5.0, "fat_g": 0.1},
    {"id": "food-cheddar", "name": "Cheddar", "serving_size": 100, "calories_per_serving": 403, "protein_g": 25.0, "carbs_g": 1.3, "fat_g": 33.0},
    {"id": "food-butter", "name": "Butter", "serving_size": 100, "calories_per_serving": 717, "protein_g": 0.9, "carbs_g": 0.1, "fat_g": 81.0},
    # ── Fruit ──
    {"id": "food-banana", "name": "Banane", "serving_size": 100, "calories_per_serving": 89, "protein_g": 1.1, "carbs_g": 23.0, "fat_g": 0.3, "fiber_g": 2.6, "sugar_g": 12.0},
    {"id": "food-apple", "name": "Apfel", "serving_size": 100, "calories_per_serving": 52, "protein_g": 0.3, "carbs_g": 14.0, "fat_g": 0.2, "fiber_g": 2.4, "sugar_g": 10.0},
    {"id": "food-orange", "name": "Orange", "serving_size": 100, "calories_per_serving": 47, "protein_g": 0.9, "carbs_g": 12.0, "fat_g": 0.1, "fiber_g": 2.4},
    {"id": "food-strawberries", "name": "Erdbeeren", "serving_size": 100, "calories_per_serving": 32, "protein_g": 0.7, "carbs_g": 7.7, "fat_g": 0.3, "fiber_g": 2.0, "sugar_g": 4.9},
    {"id": "food-blueberries", "name": "Heidelbeeren", "serving_size": 100, "calories_per_serving": 57, "protein_g": 0.7, "carbs_g": 14.0, "fat_g": 0.3, "fiber_g": 2.4, "sugar_g": 10.0},
    {"id": "food-avocado", "name": "Avocado", "serving_size": 100, "calories_per_serving": 160, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 15.0, "fiber_g": 6.7},
    # ── Vegetables ──
    {"id": "food-spinach", "name": "Spinat", "serving_size": 100, "calories_per_serving": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 2.2},
    {"id": "food-broccoli", "name": "Brokkoli", "serving_size": 100, "calories_per_serving": 34, "protein_g": 2.8, "carbs_g": 6.6, "fat_g": 0.4, "fiber_g": 2.6},
    {"id": "food-carrot", "name": "Karotte", "serving_size": 100, "calories_per_serving": 41, "protein_g": 0.9, "carbs_g": 9.6, "fat_g": 0.2, "fiber_g": 2.8, "sugar_g": 4.7},
    {"id": "food-tomato", "name": "Tomate", "serving_size": 100, "calories_per_serving": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "fiber_g": 1.2, "sugar_g": 2.6},
    {"id": "food-cucumber", "name": "Gurke", "serving_size": 100, "calories_per_serving": 15, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1},
    {"id": "food-bell-pepper", "name": "Paprika", "serving_size": 100, "calories_per_serving": 31, "protein_g": 1.0, "carbs_g": 6.0, "fat_g": 0.3, "fiber_g": 2.1},
    {"id": "food-onion", "name": "Zwiebel", "serving_size": 100, "calories_per_serving": 40, "protein_g": 1.1, "carbs_g": 9.3, "fat_g": 0.1, "fiber_g": 1.7},
    # ── Fats / Nuts / Seeds ──
    {"id": "food-olive-oil", "name": "Olivenöl", "serving_size": 100, "calories_per_serving": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0},
    {"id": "food-peanut-butter", "name": "Erdnussbutter", "serving_size": 100, "calories_per_serving": 588, "protein_g": 25.0, "carbs_g": 20.0, "fat_g": 50.0, "fiber_g": 6.0},
    {"id": "food-almonds", "name": "Mandeln", "serving_size": 100, "calories_per_serving": 579, "protein_g": 21.0, "carbs_g": 22.0, "fat_g": 50.0, "fiber_g": 12.0},
    {"id": "food-walnuts", "name": "Walnüsse", "serving_size": 100, "calories_per_serving": 654, "protein_g": 15.0, "carbs_g": 14.0, "fat_g": 65.0, "fiber_g": 6.7},
    {"id": "food-chia-seeds", "name": "Chiasamen", "serving_size": 100, "calories_per_serving": 486, "protein_g": 17.0, "carbs_g": 42.0, "fat_g": 31.0, "fiber_g": 34.0},
    {"id": "food-sunflower-seeds", "name": "Sonnenblumenkerne", "serving_size": 100, "calories_per_serving": 584, "protein_g": 21.0, "carbs_g": 20.0, "fat_g": 51.0, "fiber_g": 8.6},
    # ── Miscellaneous ──
    {"id": "food-honey", "name": "Honig", "serving_size": 100, "calories_per_serving": 304, "protein_g": 0.3, "carbs_g": 82.0, "fat_g": 0.0, "sugar_g": 82.0},
    {"id": "food-dark-chocolate", "name": "Zartbitterschokolade (70%)", "serving_size": 100, "calories_per_serving": 598, "protein_g": 7.8, "carbs_g": 46.0, "fat_g": 43.0, "fiber_g": 11.0},
    {"id": "food-oat-milk", "name": "Haferdrink", "serving_size": 100, "calories_per_serving": 47, "protein_g": 1.4, "carbs_g": 7.0, "fat_g": 1.5},
    {"id": "food-whey-protein", "name": "Whey-Protein", "serving_size": 100, "calories_per_serving": 400, "protein_g": 80.0, "carbs_g": 8.0, "fat_g": 6.0},
]
