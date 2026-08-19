"""Seed data for the common-food database (system items, shared across users).

Values are per 100 g serving size based on standard food composition databases
(Bundeslebensmittelschlüssel BLS & USDA FoodData Central).
Curated core covering ~300 fundamental whole foods and culinary staples.
"""

COMMON_FOODS: list[dict] = [
    # ══════════════════════════════════════════════════════════════════════
    # 🌾 GETREIDE, MEHLE, PASTA & PSEUDOGETREIDE
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-oatmeal", "name": "Haferflocken", "serving_size": 100, "calories_per_serving": 389, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9, "fiber_g": 10.6, "sugar_g": 1.0, "saturated_fat_g": 1.2, "sodium_mg": 2},
    {"id": "food-oat-bran", "name": "Haferkleie", "serving_size": 100, "calories_per_serving": 246, "protein_g": 17.3, "carbs_g": 66.2, "fat_g": 7.0, "fiber_g": 15.4, "sugar_g": 1.5, "saturated_fat_g": 1.3, "sodium_mg": 4},
    {"id": "food-wheat-bran", "name": "Weizenkleie", "serving_size": 100, "calories_per_serving": 216, "protein_g": 15.6, "carbs_g": 64.5, "fat_g": 4.3, "fiber_g": 42.8, "sugar_g": 0.4, "saturated_fat_g": 0.6, "sodium_mg": 9},
    {"id": "food-flour-wheat-405", "name": "Weizenmehl (Type 405)", "serving_size": 100, "calories_per_serving": 364, "protein_g": 10.3, "carbs_g": 76.3, "fat_g": 1.0, "fiber_g": 2.7, "sugar_g": 0.3, "saturated_fat_g": 0.2, "sodium_mg": 2},
    {"id": "food-flour-wheat-whole", "name": "Weizenvollkornmehl", "serving_size": 100, "calories_per_serving": 340, "protein_g": 13.2, "carbs_g": 72.0, "fat_g": 2.5, "fiber_g": 10.7, "sugar_g": 0.4, "saturated_fat_g": 0.4, "sodium_mg": 5},
    {"id": "food-flour-spelt-630", "name": "Dinkelmehl (Type 630)", "serving_size": 100, "calories_per_serving": 354, "protein_g": 12.0, "carbs_g": 72.0, "fat_g": 1.3, "fiber_g": 3.7, "sugar_g": 0.8, "saturated_fat_g": 0.2, "sodium_mg": 3},
    {"id": "food-flour-spelt-whole", "name": "Dinkelvollkornmehl", "serving_size": 100, "calories_per_serving": 348, "protein_g": 14.5, "carbs_g": 63.0, "fat_g": 2.7, "fiber_g": 8.8, "sugar_g": 1.0, "saturated_fat_g": 0.4, "sodium_mg": 4},
    {"id": "food-flour-rye-whole", "name": "Roggenvollkornmehl", "serving_size": 100, "calories_per_serving": 325, "protein_g": 9.5, "carbs_g": 66.0, "fat_g": 1.7, "fiber_g": 13.2, "sugar_g": 1.0, "saturated_fat_g": 0.2, "sodium_mg": 2},
    {"id": "food-flour-almond", "name": "Mandelmehl (entölt)", "serving_size": 100, "calories_per_serving": 365, "protein_g": 40.0, "carbs_g": 10.0, "fat_g": 12.0, "fiber_g": 20.0, "sugar_g": 6.0, "saturated_fat_g": 1.5, "sodium_mg": 10},
    {"id": "food-rice-basmati-raw", "name": "Basmatireis (roh)", "serving_size": 100, "calories_per_serving": 355, "protein_g": 8.5, "carbs_g": 77.0, "fat_g": 0.6, "fiber_g": 1.4, "sugar_g": 0.1, "saturated_fat_g": 0.2, "sodium_mg": 5},
    {"id": "food-rice-cooked", "name": "Reis (weiß, gekocht)", "serving_size": 100, "calories_per_serving": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "fiber_g": 0.4, "sugar_g": 0.1, "saturated_fat_g": 0.1, "sodium_mg": 1},
    {"id": "food-rice-brown-cooked", "name": "Vollkornreis (Naturreis, gekocht)", "serving_size": 100, "calories_per_serving": 111, "protein_g": 2.6, "carbs_g": 23.0, "fat_g": 0.9, "fiber_g": 1.8, "sugar_g": 0.4, "saturated_fat_g": 0.2, "sodium_mg": 5},
    {"id": "food-rice-jasmine-cooked", "name": "Jasminreis (gekocht)", "serving_size": 100, "calories_per_serving": 129, "protein_g": 2.4, "carbs_g": 28.5, "fat_g": 0.2, "fiber_g": 0.3, "sugar_g": 0.0, "saturated_fat_g": 0.1, "sodium_mg": 1},
    {"id": "food-pasta-raw", "name": "Hartweizen-Pasta (roh)", "serving_size": 100, "calories_per_serving": 360, "protein_g": 12.5, "carbs_g": 72.0, "fat_g": 1.5, "fiber_g": 3.0, "sugar_g": 3.0, "saturated_fat_g": 0.3, "sodium_mg": 6},
    {"id": "food-pasta-cooked", "name": "Pasta (gekocht)", "serving_size": 100, "calories_per_serving": 158, "protein_g": 5.8, "carbs_g": 31.0, "fat_g": 0.9, "fiber_g": 1.8, "sugar_g": 0.6, "saturated_fat_g": 0.2, "sodium_mg": 1},
    {"id": "food-pasta-wholewheat-cooked", "name": "Vollkornpasta (gekocht)", "serving_size": 100, "calories_per_serving": 124, "protein_g": 5.3, "carbs_g": 26.5, "fat_g": 0.5, "fiber_g": 4.5, "sugar_g": 0.8, "saturated_fat_g": 0.1, "sodium_mg": 4},
    {"id": "food-noodles-rice", "name": "Reisnudeln (gekocht)", "serving_size": 100, "calories_per_serving": 108, "protein_g": 1.8, "carbs_g": 24.0, "fat_g": 0.2, "fiber_g": 1.0, "sugar_g": 0.0, "saturated_fat_g": 0.0, "sodium_mg": 18},
    {"id": "food-noodles-soba", "name": "Soba-Nudeln (Buchweizen, gekocht)", "serving_size": 100, "calories_per_serving": 99, "protein_g": 5.1, "carbs_g": 21.4, "fat_g": 0.1, "fiber_g": 1.5, "sugar_g": 0.5, "saturated_fat_g": 0.0, "sodium_mg": 60},
    {"id": "food-quinoa-cooked", "name": "Quinoa (gekocht)", "serving_size": 100, "calories_per_serving": 120, "protein_g": 4.4, "carbs_g": 21.3, "fat_g": 1.9, "fiber_g": 2.8, "sugar_g": 0.9, "saturated_fat_g": 0.2, "sodium_mg": 7},
    {"id": "food-buckwheat-cooked", "name": "Buchweizen (gekocht)", "serving_size": 100, "calories_per_serving": 92, "protein_g": 3.4, "carbs_g": 20.0, "fat_g": 0.6, "fiber_g": 2.7, "sugar_g": 0.0, "saturated_fat_g": 0.1, "sodium_mg": 1},
    {"id": "food-couscous-cooked", "name": "Couscous (gekocht)", "serving_size": 100, "calories_per_serving": 112, "protein_g": 3.8, "carbs_g": 23.2, "fat_g": 0.2, "fiber_g": 1.4, "sugar_g": 0.1, "saturated_fat_g": 0.0, "sodium_mg": 5},
    {"id": "food-bulgur-cooked", "name": "Bulgur (gekocht)", "serving_size": 100, "calories_per_serving": 83, "protein_g": 3.1, "carbs_g": 18.6, "fat_g": 0.2, "fiber_g": 4.5, "sugar_g": 0.1, "saturated_fat_g": 0.0, "sodium_mg": 5},
    {"id": "food-millet-cooked", "name": "Hirse (gekocht)", "serving_size": 100, "calories_per_serving": 119, "protein_g": 3.5, "carbs_g": 23.7, "fat_g": 1.0, "fiber_g": 1.3, "sugar_g": 0.1, "saturated_fat_g": 0.2, "sodium_mg": 2},
    {"id": "food-polenta-cooked", "name": "Polenta / Maisgrieß (gekocht)", "serving_size": 100, "calories_per_serving": 70, "protein_g": 1.7, "carbs_g": 15.0, "fat_g": 0.3, "fiber_g": 1.1, "sugar_g": 0.2, "saturated_fat_g": 0.0, "sodium_mg": 120},
    {"id": "food-potato-cooked", "name": "Kartoffel (gekocht)", "serving_size": 100, "calories_per_serving": 87, "protein_g": 1.9, "carbs_g": 20.0, "fat_g": 0.1, "fiber_g": 1.8, "sugar_g": 0.8, "saturated_fat_g": 0.0, "sodium_mg": 4},
    {"id": "food-sweet-potato", "name": "Süßkartoffel (gegart)", "serving_size": 100, "calories_per_serving": 86, "protein_g": 1.6, "carbs_g": 20.1, "fat_g": 0.1, "fiber_g": 3.0, "sugar_g": 4.2, "saturated_fat_g": 0.0, "sodium_mg": 55},
    {"id": "food-gnocchi", "name": "Gnocchi (gekocht)", "serving_size": 100, "calories_per_serving": 135, "protein_g": 3.2, "carbs_g": 28.5, "fat_g": 0.8, "fiber_g": 1.5, "sugar_g": 0.5, "saturated_fat_g": 0.1, "sodium_mg": 240},

    # ══════════════════════════════════════════════════════════════════════
    # 🍞 BROT, BRÖTCHEN & BACKWAREN
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-wholewheat-bread", "name": "Vollkornbrot", "serving_size": 100, "calories_per_serving": 247, "protein_g": 13.0, "carbs_g": 41.0, "fat_g": 3.4, "fiber_g": 7.0, "sugar_g": 2.0, "saturated_fat_g": 0.6, "sodium_mg": 450},
    {"id": "food-rye-bread", "name": "Roggenbrot / Roggenmischbrot", "serving_size": 100, "calories_per_serving": 220, "protein_g": 6.8, "carbs_g": 45.0, "fat_g": 1.2, "fiber_g": 6.5, "sugar_g": 1.5, "saturated_fat_g": 0.2, "sodium_mg": 500},
    {"id": "food-spelt-bread", "name": "Dinkelbrot", "serving_size": 100, "calories_per_serving": 235, "protein_g": 9.2, "carbs_g": 44.0, "fat_g": 1.8, "fiber_g": 5.8, "sugar_g": 1.8, "saturated_fat_g": 0.3, "sodium_mg": 480},
    {"id": "food-pumpernickel", "name": "Pumpernickel", "serving_size": 100, "calories_per_serving": 195, "protein_g": 6.5, "carbs_g": 37.0, "fat_g": 1.4, "fiber_g": 9.5, "sugar_g": 3.0, "saturated_fat_g": 0.2, "sodium_mg": 460},
    {"id": "food-toast-wheat", "name": "Toastbrot (Weizen)", "serving_size": 100, "calories_per_serving": 265, "protein_g": 8.5, "carbs_g": 49.0, "fat_g": 3.5, "fiber_g": 2.5, "sugar_g": 4.0, "saturated_fat_g": 0.8, "sodium_mg": 480},
    {"id": "food-toast-wholewheat", "name": "Vollkorntoast", "serving_size": 100, "calories_per_serving": 250, "protein_g": 9.5, "carbs_g": 44.0, "fat_g": 3.2, "fiber_g": 6.0, "sugar_g": 3.5, "saturated_fat_g": 0.7, "sodium_mg": 460},
    {"id": "food-crispbread-rye", "name": "Knäckebrot (Roggenvollkorn)", "serving_size": 100, "calories_per_serving": 350, "protein_g": 10.0, "carbs_g": 65.0, "fat_g": 2.0, "fiber_g": 15.0, "sugar_g": 2.0, "saturated_fat_g": 0.4, "sodium_mg": 400},
    {"id": "food-bread-roll-wheat", "name": "Brötchen / Semmel (Weizen)", "serving_size": 100, "calories_per_serving": 270, "protein_g": 8.8, "carbs_g": 53.0, "fat_g": 1.8, "fiber_g": 3.0, "sugar_g": 1.5, "saturated_fat_g": 0.4, "sodium_mg": 520},
    {"id": "food-pretzel", "name": "Laugenbrezel", "serving_size": 100, "calories_per_serving": 285, "protein_g": 9.0, "carbs_g": 54.0, "fat_g": 3.0, "fiber_g": 3.2, "sugar_g": 2.2, "saturated_fat_g": 0.8, "sodium_mg": 850},
    {"id": "food-wrap-tortilla", "name": "Tortilla-Wrap (Weizen)", "serving_size": 100, "calories_per_serving": 310, "protein_g": 8.5, "carbs_g": 52.0, "fat_g": 7.0, "fiber_g": 2.8, "sugar_g": 2.0, "saturated_fat_g": 2.5, "sodium_mg": 550},
    {"id": "food-pita-bread", "name": "Pita / Fladenbrot", "serving_size": 100, "calories_per_serving": 260, "protein_g": 8.5, "carbs_g": 51.0, "fat_g": 1.5, "fiber_g": 2.5, "sugar_g": 1.8, "saturated_fat_g": 0.3, "sodium_mg": 480},
    {"id": "food-rice-cake", "name": "Reiswaffeln (Natur)", "serving_size": 100, "calories_per_serving": 387, "protein_g": 8.0, "carbs_g": 82.0, "fat_g": 2.5, "fiber_g": 3.5, "sugar_g": 0.5, "saturated_fat_g": 0.6, "sodium_mg": 10},
    {"id": "food-corn-cake", "name": "Maiswaffeln", "serving_size": 100, "calories_per_serving": 380, "protein_g": 7.5, "carbs_g": 81.0, "fat_g": 1.8, "fiber_g": 4.0, "sugar_g": 0.8, "saturated_fat_g": 0.4, "sodium_mg": 80},

    # ══════════════════════════════════════════════════════════════════════
    # 🥩 FLEISCH & GEFLÜGEL
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-chicken-breast", "name": "Hähnchenbrustfilet (gebraten)", "serving_size": 100, "calories_per_serving": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 1.0, "sodium_mg": 74},
    {"id": "food-chicken-breast-raw", "name": "Hähnchenbrustfilet (roh)", "serving_size": 100, "calories_per_serving": 110, "protein_g": 23.0, "carbs_g": 0.0, "fat_g": 1.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.4, "sodium_mg": 65},
    {"id": "food-chicken-thigh", "name": "Hähnchenschenkel (ohne Haut, gegart)", "serving_size": 100, "calories_per_serving": 180, "protein_g": 24.5, "carbs_g": 0.0, "fat_g": 8.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 2.3, "sodium_mg": 85},
    {"id": "food-turkey-breast", "name": "Putenbrustfilet (roh)", "serving_size": 100, "calories_per_serving": 107, "protein_g": 24.0, "carbs_g": 0.0, "fat_g": 1.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.3, "sodium_mg": 60},
    {"id": "food-duck-breast", "name": "Entenbrust (ohne Haut, gegart)", "serving_size": 100, "calories_per_serving": 140, "protein_g": 28.0, "carbs_g": 0.0, "fat_g": 2.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.8, "sodium_mg": 65},
    {"id": "food-beef-fillet", "name": "Rinderfilet (gegart)", "serving_size": 100, "calories_per_serving": 190, "protein_g": 29.0, "carbs_g": 0.0, "fat_g": 8.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 3.2, "sodium_mg": 55},
    {"id": "food-beef-rumpsteak", "name": "Rumpsteak (gebraten)", "serving_size": 100, "calories_per_serving": 210, "protein_g": 28.0, "carbs_g": 0.0, "fat_g": 10.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 4.5, "sodium_mg": 60},
    {"id": "food-ground-beef", "name": "Rinderhackfleisch (mager, roh)", "serving_size": 100, "calories_per_serving": 180, "protein_g": 21.0, "carbs_g": 0.0, "fat_g": 10.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 4.2, "sodium_mg": 70},
    {"id": "food-ground-beef-mixed", "name": "Hackfleisch (gemischt, Rind/Schwein)", "serving_size": 100, "calories_per_serving": 235, "protein_g": 18.5, "carbs_g": 0.0, "fat_g": 17.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 7.0, "sodium_mg": 75},
    {"id": "food-pork-tenderloin", "name": "Schweinefilet (roh)", "serving_size": 100, "calories_per_serving": 120, "protein_g": 22.0, "carbs_g": 0.0, "fat_g": 3.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 1.1, "sodium_mg": 55},
    {"id": "food-pork-schnitzel", "name": "Schweineschnitzel (mager, roh)", "serving_size": 100, "calories_per_serving": 115, "protein_g": 22.5, "carbs_g": 0.0, "fat_g": 2.2, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.8, "sodium_mg": 60},
    {"id": "food-ham-cooked", "name": "Kochschinken / Hinterschinken", "serving_size": 100, "calories_per_serving": 110, "protein_g": 20.0, "carbs_g": 1.0, "fat_g": 3.0, "fiber_g": 0.0, "sugar_g": 0.5, "saturated_fat_g": 1.2, "sodium_mg": 950},
    {"id": "food-ham-raw", "name": "Rohschinken / Parmaschinken", "serving_size": 100, "calories_per_serving": 225, "protein_g": 26.0, "carbs_g": 0.5, "fat_g": 13.0, "fiber_g": 0.0, "sugar_g": 0.1, "saturated_fat_g": 5.0, "sodium_mg": 1800},
    {"id": "food-turkey-slices", "name": "Putenbrust-Aufschnitt", "serving_size": 100, "calories_per_serving": 105, "protein_g": 21.0, "carbs_g": 1.0, "fat_g": 2.0, "fiber_g": 0.0, "sugar_g": 0.5, "saturated_fat_g": 0.6, "sodium_mg": 900},
    {"id": "food-bacon", "name": "Bacon / Frühstücksspeck", "serving_size": 100, "calories_per_serving": 400, "protein_g": 14.0, "carbs_g": 0.5, "fat_g": 38.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 14.0, "sodium_mg": 1200},
    {"id": "food-wiener-sausage", "name": "Wiener Würstchen", "serving_size": 100, "calories_per_serving": 280, "protein_g": 12.5, "carbs_g": 1.0, "fat_g": 25.0, "fiber_g": 0.0, "sugar_g": 0.5, "saturated_fat_g": 9.5, "sodium_mg": 850},
    {"id": "food-lamb-chop", "name": "Lammkotelett (gegart)", "serving_size": 100, "calories_per_serving": 230, "protein_g": 25.0, "carbs_g": 0.0, "fat_g": 14.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 6.0, "sodium_mg": 70},

    # ══════════════════════════════════════════════════════════════════════
    # 🐟 FISCH & MEERESFRÜCHTE
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-salmon", "name": "Lachsfilet (frisch / gebraten)", "serving_size": 100, "calories_per_serving": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 2.5, "sodium_mg": 55},
    {"id": "food-salmon-smoked", "name": "Räucherlachs", "serving_size": 100, "calories_per_serving": 180, "protein_g": 21.5, "carbs_g": 0.0, "fat_g": 10.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 2.0, "sodium_mg": 1200},
    {"id": "food-tuna", "name": "Thunfisch (frisch, roh)", "serving_size": 100, "calories_per_serving": 132, "protein_g": 28.0, "carbs_g": 0.0, "fat_g": 1.3, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.4, "sodium_mg": 45},
    {"id": "food-tuna-canned-water", "name": "Thunfisch (Dose, im eigenen Saft)", "serving_size": 100, "calories_per_serving": 110, "protein_g": 25.5, "carbs_g": 0.0, "fat_g": 0.8, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.2, "sodium_mg": 350},
    {"id": "food-tuna-canned-oil", "name": "Thunfisch (Dose, in Öl abgetropft)", "serving_size": 100, "calories_per_serving": 190, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 9.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 1.5, "sodium_mg": 380},
    {"id": "food-cod", "name": "Kabeljau / Dorsch (roh)", "serving_size": 100, "calories_per_serving": 82, "protein_g": 17.8, "carbs_g": 0.0, "fat_g": 0.7, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.1, "sodium_mg": 70},
    {"id": "food-pollock", "name": "Seelachs (Alaska, roh)", "serving_size": 100, "calories_per_serving": 78, "protein_g": 17.0, "carbs_g": 0.0, "fat_g": 0.8, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.2, "sodium_mg": 85},
    {"id": "food-trout", "name": "Forelle (Regenbogenforelle, roh)", "serving_size": 100, "calories_per_serving": 120, "protein_g": 19.5, "carbs_g": 0.0, "fat_g": 4.5, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 1.1, "sodium_mg": 50},
    {"id": "food-mackerel", "name": "Makrele (roh)", "serving_size": 100, "calories_per_serving": 205, "protein_g": 18.6, "carbs_g": 0.0, "fat_g": 13.9, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 3.3, "sodium_mg": 90},
    {"id": "food-sardines-canned", "name": "Sardinen (Dose, in Öl)", "serving_size": 100, "calories_per_serving": 210, "protein_g": 24.0, "carbs_g": 0.0, "fat_g": 12.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 2.8, "sodium_mg": 450},
    {"id": "food-shrimp", "name": "Garnelen / Shrimps (gekocht)", "serving_size": 100, "calories_per_serving": 99, "protein_g": 24.0, "carbs_g": 0.2, "fat_g": 0.3, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.1, "sodium_mg": 220},
    {"id": "food-squid", "name": "Tintenfisch / Calamari (roh)", "serving_size": 100, "calories_per_serving": 92, "protein_g": 15.6, "carbs_g": 3.1, "fat_g": 1.4, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.4, "sodium_mg": 44},
    {"id": "food-mussels", "name": "Miesmuscheln (gekocht)", "serving_size": 100, "calories_per_serving": 86, "protein_g": 12.0, "carbs_g": 3.7, "fat_g": 2.2, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.4, "sodium_mg": 280},

    # ══════════════════════════════════════════════════════════════════════
    # 🌱 VEGETARISCHE / VEGANE PROTEINE & EIER
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-eggs", "name": "Eier (Hühnerei, ganz)", "serving_size": 100, "calories_per_serving": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0, "fiber_g": 0.0, "sugar_g": 0.4, "saturated_fat_g": 3.3, "sodium_mg": 124},
    {"id": "food-egg-white", "name": "Eiklar / Eiweiß", "serving_size": 100, "calories_per_serving": 52, "protein_g": 11.0, "carbs_g": 0.7, "fat_g": 0.2, "fiber_g": 0.0, "sugar_g": 0.7, "saturated_fat_g": 0.0, "sodium_mg": 166},
    {"id": "food-egg-yolk", "name": "Eigelb", "serving_size": 100, "calories_per_serving": 322, "protein_g": 16.0, "carbs_g": 3.6, "fat_g": 27.0, "fiber_g": 0.0, "sugar_g": 0.6, "saturated_fat_g": 9.6, "sodium_mg": 48},
    {"id": "food-tofu", "name": "Tofu (Natur)", "serving_size": 100, "calories_per_serving": 76, "protein_g": 8.0, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3, "sugar_g": 0.5, "saturated_fat_g": 0.7, "sodium_mg": 7},
    {"id": "food-tofu-smoked", "name": "Räuchertofu", "serving_size": 100, "calories_per_serving": 140, "protein_g": 16.0, "carbs_g": 2.0, "fat_g": 7.5, "fiber_g": 1.5, "sugar_g": 0.8, "saturated_fat_g": 1.2, "sodium_mg": 450},
    {"id": "food-tofu-silken", "name": "Seidentofu", "serving_size": 100, "calories_per_serving": 55, "protein_g": 5.5, "carbs_g": 1.5, "fat_g": 2.8, "fiber_g": 0.2, "sugar_g": 0.8, "saturated_fat_g": 0.4, "sodium_mg": 15},
    {"id": "food-tempeh", "name": "Tempeh", "serving_size": 100, "calories_per_serving": 192, "protein_g": 20.3, "carbs_g": 7.6, "fat_g": 10.8, "fiber_g": 4.0, "sugar_g": 0.5, "saturated_fat_g": 2.2, "sodium_mg": 9},
    {"id": "food-seitan", "name": "Seitan / Weizenprotein", "serving_size": 100, "calories_per_serving": 140, "protein_g": 28.0, "carbs_g": 4.0, "fat_g": 1.5, "fiber_g": 1.0, "sugar_g": 0.5, "saturated_fat_g": 0.3, "sodium_mg": 380},
    {"id": "food-soy-granulate", "name": "Sojagranulat / Sojaschnetzel (trocken)", "serving_size": 100, "calories_per_serving": 315, "protein_g": 50.0, "carbs_g": 15.0, "fat_g": 2.0, "fiber_g": 18.0, "sugar_g": 6.0, "saturated_fat_g": 0.5, "sodium_mg": 20},

    # ══════════════════════════════════════════════════════════════════════
    # 🫘 HÜLSENFRÜCHTE
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-lentils-cooked", "name": "Linsen (braun / Berglinsen, gekocht)", "serving_size": 100, "calories_per_serving": 116, "protein_g": 9.0, "carbs_g": 20.0, "fat_g": 0.4, "fiber_g": 7.9, "sugar_g": 1.8, "saturated_fat_g": 0.1, "sodium_mg": 2},
    {"id": "food-lentils-red-raw", "name": "Rote Linsen (trocken)", "serving_size": 100, "calories_per_serving": 330, "protein_g": 24.0, "carbs_g": 50.0, "fat_g": 1.5, "fiber_g": 11.0, "sugar_g": 2.0, "saturated_fat_g": 0.3, "sodium_mg": 10},
    {"id": "food-lentils-red-cooked", "name": "Rote Linsen (gekocht)", "serving_size": 100, "calories_per_serving": 118, "protein_g": 8.8, "carbs_g": 18.5, "fat_g": 0.6, "fiber_g": 4.5, "sugar_g": 1.2, "saturated_fat_g": 0.1, "sodium_mg": 5},
    {"id": "food-chickpeas-cooked", "name": "Kichererbsen (Dose / gekocht)", "serving_size": 100, "calories_per_serving": 130, "protein_g": 7.5, "carbs_g": 19.5, "fat_g": 2.4, "fiber_g": 6.0, "sugar_g": 1.0, "saturated_fat_g": 0.3, "sodium_mg": 180},
    {"id": "food-kidney-beans", "name": "Kidneybohnen (Dose / gegart)", "serving_size": 100, "calories_per_serving": 115, "protein_g": 8.0, "carbs_g": 16.5, "fat_g": 0.6, "fiber_g": 6.5, "sugar_g": 0.8, "saturated_fat_g": 0.1, "sodium_mg": 220},
    {"id": "food-black-beans", "name": "Schwarze Bohnen (gekocht)", "serving_size": 100, "calories_per_serving": 132, "protein_g": 8.9, "carbs_g": 23.7, "fat_g": 0.5, "fiber_g": 8.7, "sugar_g": 0.3, "saturated_fat_g": 0.1, "sodium_mg": 2},
    {"id": "food-white-beans", "name": "Weiße Bohnen / Cannellini (gekocht)", "serving_size": 100, "calories_per_serving": 139, "protein_g": 9.7, "carbs_g": 25.0, "fat_g": 0.5, "fiber_g": 6.3, "sugar_g": 0.4, "saturated_fat_g": 0.1, "sodium_mg": 5},
    {"id": "food-edamame", "name": "Edamame (Sojabohnen, gegart)", "serving_size": 100, "calories_per_serving": 121, "protein_g": 11.9, "carbs_g": 8.9, "fat_g": 5.2, "fiber_g": 5.2, "sugar_g": 2.2, "saturated_fat_g": 0.7, "sodium_mg": 6},
    {"id": "food-green-peas", "name": "Erbsen (grün, TK / gekocht)", "serving_size": 100, "calories_per_serving": 81, "protein_g": 5.4, "carbs_g": 14.5, "fat_g": 0.4, "fiber_g": 5.7, "sugar_g": 5.7, "saturated_fat_g": 0.1, "sodium_mg": 5},

    # ══════════════════════════════════════════════════════════════════════
    # 🥛 MILCHPRODUKTE & PFLANZLICHE ALTERNATIVEN
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-milk-whole", "name": "Milch (3,5% Fett)", "serving_size": 100, "calories_per_serving": 64, "protein_g": 3.4, "carbs_g": 4.8, "fat_g": 3.5, "fiber_g": 0.0, "sugar_g": 4.8, "saturated_fat_g": 2.3, "sodium_mg": 44},
    {"id": "food-milk-skim", "name": "Milch (fettarm, 1,5% Fett)", "serving_size": 100, "calories_per_serving": 47, "protein_g": 3.4, "carbs_g": 4.9, "fat_g": 1.5, "fiber_g": 0.0, "sugar_g": 4.9, "saturated_fat_g": 1.0, "sodium_mg": 45},
    {"id": "food-quark-lowfat", "name": "Magerquark (Speisequark Magerstufe)", "serving_size": 100, "calories_per_serving": 68, "protein_g": 12.5, "carbs_g": 4.0, "fat_g": 0.2, "fiber_g": 0.0, "sugar_g": 4.0, "saturated_fat_g": 0.1, "sodium_mg": 35},
    {"id": "food-skyr", "name": "Skyr (Natur)", "serving_size": 100, "calories_per_serving": 65, "protein_g": 11.0, "carbs_g": 4.0, "fat_g": 0.2, "fiber_g": 0.0, "sugar_g": 4.0, "saturated_fat_g": 0.1, "sodium_mg": 40},
    {"id": "food-greek-yogurt", "name": "Griechischer Joghurt (10% Fett)", "serving_size": 100, "calories_per_serving": 120, "protein_g": 6.5, "carbs_g": 3.5, "fat_g": 10.0, "fiber_g": 0.0, "sugar_g": 3.5, "saturated_fat_g": 6.5, "sodium_mg": 40},
    {"id": "food-greek-yogurt-0", "name": "Griechischer Joghurt (0% Fett)", "serving_size": 100, "calories_per_serving": 59, "protein_g": 10.3, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 0.0, "sugar_g": 3.6, "saturated_fat_g": 0.1, "sodium_mg": 40},
    {"id": "food-yogurt-natural-35", "name": "Joghurt (Natur, 3,5% Fett)", "serving_size": 100, "calories_per_serving": 66, "protein_g": 3.8, "carbs_g": 5.0, "fat_g": 3.5, "fiber_g": 0.0, "sugar_g": 5.0, "saturated_fat_g": 2.2, "sodium_mg": 50},
    {"id": "food-yogurt-natural-15", "name": "Joghurt (Natur, 1,5% Fett)", "serving_size": 100, "calories_per_serving": 48, "protein_g": 4.0, "carbs_g": 5.2, "fat_g": 1.5, "fiber_g": 0.0, "sugar_g": 5.2, "saturated_fat_g": 1.0, "sodium_mg": 52},
    {"id": "food-cottage-cheese", "name": "Hüttenkäse / Körniger Frischkäse", "serving_size": 100, "calories_per_serving": 98, "protein_g": 12.0, "carbs_g": 2.5, "fat_g": 4.3, "fiber_g": 0.0, "sugar_g": 2.5, "saturated_fat_g": 2.8, "sodium_mg": 360},
    {"id": "food-cottage-cheese-light", "name": "Hüttenkäse (Magerstufe / Light)", "serving_size": 100, "calories_per_serving": 72, "protein_g": 13.0, "carbs_g": 2.0, "fat_g": 1.0, "fiber_g": 0.0, "sugar_g": 2.0, "saturated_fat_g": 0.6, "sodium_mg": 380},
    {"id": "food-buttermilk", "name": "Reine Buttermilch", "serving_size": 100, "calories_per_serving": 38, "protein_g": 3.4, "carbs_g": 4.0, "fat_g": 0.5, "fiber_g": 0.0, "sugar_g": 4.0, "saturated_fat_g": 0.3, "sodium_mg": 55},
    {"id": "food-kefir", "name": "Kefir", "serving_size": 100, "calories_per_serving": 55, "protein_g": 3.5, "carbs_g": 4.2, "fat_g": 3.0, "fiber_g": 0.0, "sugar_g": 4.2, "saturated_fat_g": 1.8, "sodium_mg": 45},
    {"id": "food-cheddar", "name": "Cheddar", "serving_size": 100, "calories_per_serving": 403, "protein_g": 25.0, "carbs_g": 1.3, "fat_g": 33.0, "fiber_g": 0.0, "sugar_g": 0.5, "saturated_fat_g": 21.0, "sodium_mg": 640},
    {"id": "food-gouda", "name": "Gouda (jung / 48% F.i.Tr.)", "serving_size": 100, "calories_per_serving": 356, "protein_g": 24.0, "carbs_g": 0.0, "fat_g": 29.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 19.0, "sodium_mg": 700},
    {"id": "food-parmesan", "name": "Parmesan / Grana Padano", "serving_size": 100, "calories_per_serving": 431, "protein_g": 38.5, "carbs_g": 4.1, "fat_g": 28.6, "fiber_g": 0.0, "sugar_g": 0.8, "saturated_fat_g": 18.0, "sodium_mg": 1500},
    {"id": "food-mozzarella", "name": "Mozzarella (Kuhmilch)", "serving_size": 100, "calories_per_serving": 280, "protein_g": 20.0, "carbs_g": 1.5, "fat_g": 22.0, "fiber_g": 0.0, "sugar_g": 1.0, "saturated_fat_g": 14.0, "sodium_mg": 400},
    {"id": "food-mozzarella-light", "name": "Mozzarella (Light)", "serving_size": 100, "calories_per_serving": 165, "protein_g": 20.5, "carbs_g": 1.5, "fat_g": 8.5, "fiber_g": 0.0, "sugar_g": 1.5, "saturated_fat_g": 5.5, "sodium_mg": 420},
    {"id": "food-feta", "name": "Feta (Original Schaf/Ziege)", "serving_size": 100, "calories_per_serving": 264, "protein_g": 14.2, "carbs_g": 1.0, "fat_g": 21.3, "fiber_g": 0.0, "sugar_g": 1.0, "saturated_fat_g": 15.0, "sodium_mg": 1100},
    {"id": "food-cream-cheese", "name": "Frischkäse (Natur, Doppelrahm)", "serving_size": 100, "calories_per_serving": 255, "protein_g": 6.5, "carbs_g": 3.5, "fat_g": 24.5, "fiber_g": 0.0, "sugar_g": 3.5, "saturated_fat_g": 16.0, "sodium_mg": 320},
    {"id": "food-ricotta", "name": "Ricotta", "serving_size": 100, "calories_per_serving": 145, "protein_g": 9.0, "carbs_g": 4.5, "fat_g": 10.0, "fiber_g": 0.0, "sugar_g": 3.0, "saturated_fat_g": 6.5, "sodium_mg": 100},
    {"id": "food-butter", "name": "Butter", "serving_size": 100, "calories_per_serving": 717, "protein_g": 0.9, "carbs_g": 0.7, "fat_g": 81.0, "fiber_g": 0.0, "sugar_g": 0.7, "saturated_fat_g": 51.0, "sodium_mg": 11},
    {"id": "food-sour-cream", "name": "Saure Sahne (10% Fett)", "serving_size": 100, "calories_per_serving": 115, "protein_g": 3.1, "carbs_g": 4.0, "fat_g": 10.0, "fiber_g": 0.0, "sugar_g": 4.0, "saturated_fat_g": 6.5, "sodium_mg": 40},
    {"id": "food-heavy-cream", "name": "Schlagsahne (30% Fett)", "serving_size": 100, "calories_per_serving": 290, "protein_g": 2.4, "carbs_g": 3.3, "fat_g": 30.0, "fiber_g": 0.0, "sugar_g": 3.3, "saturated_fat_g": 19.5, "sodium_mg": 35},
    {"id": "food-oat-milk", "name": "Haferdrink (ungesüßt)", "serving_size": 100, "calories_per_serving": 42, "protein_g": 0.8, "carbs_g": 6.5, "fat_g": 1.4, "fiber_g": 0.8, "sugar_g": 4.0, "saturated_fat_g": 0.2, "sodium_mg": 40},
    {"id": "food-almond-milk", "name": "Mandeldrink (ungesüßt)", "serving_size": 100, "calories_per_serving": 15, "protein_g": 0.5, "carbs_g": 0.2, "fat_g": 1.2, "fiber_g": 0.3, "sugar_g": 0.1, "saturated_fat_g": 0.1, "sodium_mg": 50},
    {"id": "food-soy-milk", "name": "Sojadrink (ungesüßt)", "serving_size": 100, "calories_per_serving": 39, "protein_g": 3.3, "carbs_g": 0.6, "fat_g": 2.1, "fiber_g": 0.6, "sugar_g": 0.5, "saturated_fat_g": 0.3, "sodium_mg": 40},
    {"id": "food-coconut-milk-canned", "name": "Kokosmilch (Dose)", "serving_size": 100, "calories_per_serving": 185, "protein_g": 1.8, "carbs_g": 2.5, "fat_g": 19.0, "fiber_g": 0.0, "sugar_g": 2.0, "saturated_fat_g": 17.0, "sodium_mg": 15},

    # ══════════════════════════════════════════════════════════════════════
    # 🍎 OBST & BEEREN
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-banana", "name": "Banane", "serving_size": 100, "calories_per_serving": 89, "protein_g": 1.1, "carbs_g": 22.8, "fat_g": 0.3, "fiber_g": 2.6, "sugar_g": 12.2, "saturated_fat_g": 0.1, "sodium_mg": 1},
    {"id": "food-apple", "name": "Apfel (mit Schale)", "serving_size": 100, "calories_per_serving": 52, "protein_g": 0.3, "carbs_g": 13.8, "fat_g": 0.2, "fiber_g": 2.4, "sugar_g": 10.4, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-pear", "name": "Birne", "serving_size": 100, "calories_per_serving": 57, "protein_g": 0.4, "carbs_g": 15.2, "fat_g": 0.1, "fiber_g": 3.1, "sugar_g": 9.8, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-orange", "name": "Orange", "serving_size": 100, "calories_per_serving": 47, "protein_g": 0.9, "carbs_g": 11.8, "fat_g": 0.1, "fiber_g": 2.4, "sugar_g": 9.4, "saturated_fat_g": 0.0, "sodium_mg": 0},
    {"id": "food-mandarin", "name": "Mandarine / Clementine", "serving_size": 100, "calories_per_serving": 53, "protein_g": 0.8, "carbs_g": 13.3, "fat_g": 0.3, "fiber_g": 1.8, "sugar_g": 10.6, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-grapefruit", "name": "Grapefruit", "serving_size": 100, "calories_per_serving": 42, "protein_g": 0.8, "carbs_g": 10.7, "fat_g": 0.1, "fiber_g": 1.6, "sugar_g": 7.0, "saturated_fat_g": 0.0, "sodium_mg": 0},
    {"id": "food-lemon", "name": "Zitrone (Frucht / Saft)", "serving_size": 100, "calories_per_serving": 29, "protein_g": 1.1, "carbs_g": 9.3, "fat_g": 0.3, "fiber_g": 2.8, "sugar_g": 2.5, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-strawberries", "name": "Erdbeeren", "serving_size": 100, "calories_per_serving": 32, "protein_g": 0.7, "carbs_g": 7.7, "fat_g": 0.3, "fiber_g": 2.0, "sugar_g": 4.9, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-blueberries", "name": "Heidelbeeren / Blaubeeren", "serving_size": 100, "calories_per_serving": 57, "protein_g": 0.7, "carbs_g": 14.5, "fat_g": 0.3, "fiber_g": 2.4, "sugar_g": 10.0, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-raspberries", "name": "Himbeeren", "serving_size": 100, "calories_per_serving": 52, "protein_g": 1.2, "carbs_g": 11.9, "fat_g": 0.7, "fiber_g": 6.5, "sugar_g": 4.4, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-blackberries", "name": "Brombeeren", "serving_size": 100, "calories_per_serving": 43, "protein_g": 1.4, "carbs_g": 9.6, "fat_g": 0.5, "fiber_g": 5.3, "sugar_g": 4.9, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-grapes", "name": "Weintrauben (hell / dunkel)", "serving_size": 100, "calories_per_serving": 69, "protein_g": 0.7, "carbs_g": 18.1, "fat_g": 0.2, "fiber_g": 0.9, "sugar_g": 15.5, "saturated_fat_g": 0.1, "sodium_mg": 2},
    {"id": "food-cherries", "name": "Süßkirschen", "serving_size": 100, "calories_per_serving": 63, "protein_g": 1.1, "carbs_g": 16.0, "fat_g": 0.2, "fiber_g": 2.1, "sugar_g": 12.8, "saturated_fat_g": 0.0, "sodium_mg": 0},
    {"id": "food-peach", "name": "Pfirsich / Nektarine", "serving_size": 100, "calories_per_serving": 44, "protein_g": 0.9, "carbs_g": 10.6, "fat_g": 0.3, "fiber_g": 1.7, "sugar_g": 8.4, "saturated_fat_g": 0.1, "sodium_mg": 0},
    {"id": "food-apricot", "name": "Aprikose", "serving_size": 100, "calories_per_serving": 48, "protein_g": 1.4, "carbs_g": 11.1, "fat_g": 0.4, "fiber_g": 2.0, "sugar_g": 9.2, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-plum", "name": "Pflaume / Zwetschge", "serving_size": 100, "calories_per_serving": 46, "protein_g": 0.7, "carbs_g": 11.4, "fat_g": 0.3, "fiber_g": 1.4, "sugar_g": 9.9, "saturated_fat_g": 0.0, "sodium_mg": 0},
    {"id": "food-kiwi", "name": "Kiwi", "serving_size": 100, "calories_per_serving": 61, "protein_g": 1.1, "carbs_g": 14.7, "fat_g": 0.5, "fiber_g": 3.0, "sugar_g": 9.0, "saturated_fat_g": 0.0, "sodium_mg": 3},
    {"id": "food-pineapple", "name": "Ananas (frisch)", "serving_size": 100, "calories_per_serving": 50, "protein_g": 0.5, "carbs_g": 13.1, "fat_g": 0.1, "fiber_g": 1.4, "sugar_g": 9.9, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-mango", "name": "Mango", "serving_size": 100, "calories_per_serving": 60, "protein_g": 0.8, "carbs_g": 15.0, "fat_g": 0.4, "fiber_g": 1.6, "sugar_g": 13.7, "saturated_fat_g": 0.1, "sodium_mg": 1},
    {"id": "food-watermelon", "name": "Wassermelone", "serving_size": 100, "calories_per_serving": 30, "protein_g": 0.6, "carbs_g": 7.6, "fat_g": 0.2, "fiber_g": 0.4, "sugar_g": 6.2, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-cantaloupe", "name": "Honigmelone / Cantaloupe", "serving_size": 100, "calories_per_serving": 34, "protein_g": 0.8, "carbs_g": 8.2, "fat_g": 0.2, "fiber_g": 0.9, "sugar_g": 7.9, "saturated_fat_g": 0.0, "sodium_mg": 16},
    {"id": "food-avocado", "name": "Avocado", "serving_size": 100, "calories_per_serving": 160, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 14.7, "fiber_g": 6.7, "sugar_g": 0.7, "saturated_fat_g": 2.1, "sodium_mg": 7},
    {"id": "food-dates-medjool", "name": "Datteln (Medjool, getrocknet)", "serving_size": 100, "calories_per_serving": 277, "protein_g": 1.8, "carbs_g": 75.0, "fat_g": 0.2, "fiber_g": 6.7, "sugar_g": 66.5, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-raisins", "name": "Rosinen / Sultaninen", "serving_size": 100, "calories_per_serving": 299, "protein_g": 3.1, "carbs_g": 79.2, "fat_g": 0.5, "fiber_g": 3.7, "sugar_g": 59.2, "saturated_fat_g": 0.1, "sodium_mg": 11},

    # ══════════════════════════════════════════════════════════════════════
    # 🥦 GEMÜSE & SALATE
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-spinach", "name": "Spinat (frisch)", "serving_size": 100, "calories_per_serving": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 2.2, "sugar_g": 0.4, "saturated_fat_g": 0.1, "sodium_mg": 79},
    {"id": "food-spinach-frozen", "name": "Blattspinat (TK / gegart)", "serving_size": 100, "calories_per_serving": 25, "protein_g": 3.0, "carbs_g": 2.5, "fat_g": 0.5, "fiber_g": 2.5, "sugar_g": 0.5, "saturated_fat_g": 0.1, "sodium_mg": 70},
    {"id": "food-kale", "name": "Grünkohl", "serving_size": 100, "calories_per_serving": 49, "protein_g": 4.3, "carbs_g": 8.8, "fat_g": 0.9, "fiber_g": 3.6, "sugar_g": 2.3, "saturated_fat_g": 0.1, "sodium_mg": 38},
    {"id": "food-rucola", "name": "Rucola", "serving_size": 100, "calories_per_serving": 25, "protein_g": 2.6, "carbs_g": 3.7, "fat_g": 0.7, "fiber_g": 1.6, "sugar_g": 2.1, "saturated_fat_g": 0.1, "sodium_mg": 27},
    {"id": "food-field-salad", "name": "Feldsalat", "serving_size": 100, "calories_per_serving": 14, "protein_g": 2.0, "carbs_g": 0.8, "fat_g": 0.4, "fiber_g": 1.5, "sugar_g": 0.8, "saturated_fat_g": 0.1, "sodium_mg": 4},
    {"id": "food-lettuce-iceberg", "name": "Eisbergsalat", "serving_size": 100, "calories_per_serving": 14, "protein_g": 0.9, "carbs_g": 3.0, "fat_g": 0.1, "fiber_g": 1.2, "sugar_g": 2.0, "saturated_fat_g": 0.0, "sodium_mg": 10},
    {"id": "food-lettuce-romaine", "name": "Romanasalat", "serving_size": 100, "calories_per_serving": 17, "protein_g": 1.2, "carbs_g": 3.3, "fat_g": 0.3, "fiber_g": 2.1, "sugar_g": 1.2, "saturated_fat_g": 0.0, "sodium_mg": 8},
    {"id": "food-broccoli", "name": "Brokkoli (roh / gedämpft)", "serving_size": 100, "calories_per_serving": 34, "protein_g": 2.8, "carbs_g": 6.6, "fat_g": 0.4, "fiber_g": 2.6, "sugar_g": 1.7, "saturated_fat_g": 0.1, "sodium_mg": 33},
    {"id": "food-cauliflower", "name": "Blumenkohl (roh / gedämpft)", "serving_size": 100, "calories_per_serving": 25, "protein_g": 1.9, "carbs_g": 5.0, "fat_g": 0.3, "fiber_g": 2.0, "sugar_g": 1.9, "saturated_fat_g": 0.1, "sodium_mg": 30},
    {"id": "food-brussels-sprouts", "name": "Rosenkohl (gekocht)", "serving_size": 100, "calories_per_serving": 43, "protein_g": 3.4, "carbs_g": 9.0, "fat_g": 0.3, "fiber_g": 3.8, "sugar_g": 2.2, "saturated_fat_g": 0.1, "sodium_mg": 25},
    {"id": "food-cabbage-white", "name": "Weißkohl / Spitzkohl", "serving_size": 100, "calories_per_serving": 25, "protein_g": 1.3, "carbs_g": 5.8, "fat_g": 0.1, "fiber_g": 2.5, "sugar_g": 3.2, "saturated_fat_g": 0.0, "sodium_mg": 18},
    {"id": "food-cabbage-red", "name": "Rotkohl", "serving_size": 100, "calories_per_serving": 31, "protein_g": 1.4, "carbs_g": 7.4, "fat_g": 0.2, "fiber_g": 2.1, "sugar_g": 3.8, "saturated_fat_g": 0.0, "sodium_mg": 27},
    {"id": "food-kohlrabi", "name": "Kohlrabi", "serving_size": 100, "calories_per_serving": 27, "protein_g": 1.7, "carbs_g": 6.2, "fat_g": 0.1, "fiber_g": 3.6, "sugar_g": 2.6, "saturated_fat_g": 0.0, "sodium_mg": 20},
    {"id": "food-carrot", "name": "Karotte / Möhre", "serving_size": 100, "calories_per_serving": 41, "protein_g": 0.9, "carbs_g": 9.6, "fat_g": 0.2, "fiber_g": 2.8, "sugar_g": 4.7, "saturated_fat_g": 0.0, "sodium_mg": 69},
    {"id": "food-tomato", "name": "Tomate", "serving_size": 100, "calories_per_serving": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "fiber_g": 1.2, "sugar_g": 2.6, "saturated_fat_g": 0.0, "sodium_mg": 5},
    {"id": "food-tomato-passata", "name": "Passierte Tomaten / Tomatenstücke (Dose)", "serving_size": 100, "calories_per_serving": 24, "protein_g": 1.3, "carbs_g": 4.2, "fat_g": 0.2, "fiber_g": 1.2, "sugar_g": 3.8, "saturated_fat_g": 0.0, "sodium_mg": 20},
    {"id": "food-cucumber", "name": "Gurke / Salatgurke", "serving_size": 100, "calories_per_serving": 15, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1, "fiber_g": 0.5, "sugar_g": 1.7, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-bell-pepper", "name": "Paprika (rot / gelb)", "serving_size": 100, "calories_per_serving": 31, "protein_g": 1.0, "carbs_g": 6.0, "fat_g": 0.3, "fiber_g": 2.1, "sugar_g": 4.2, "saturated_fat_g": 0.1, "sodium_mg": 4},
    {"id": "food-bell-pepper-green", "name": "Paprika (grün)", "serving_size": 100, "calories_per_serving": 20, "protein_g": 0.9, "carbs_g": 4.6, "fat_g": 0.2, "fiber_g": 1.7, "sugar_g": 2.4, "saturated_fat_g": 0.0, "sodium_mg": 3},
    {"id": "food-zucchini", "name": "Zucchini", "serving_size": 100, "calories_per_serving": 17, "protein_g": 1.2, "carbs_g": 3.1, "fat_g": 0.3, "fiber_g": 1.0, "sugar_g": 2.5, "saturated_fat_g": 0.1, "sodium_mg": 8},
    {"id": "food-eggplant", "name": "Aubergine", "serving_size": 100, "calories_per_serving": 25, "protein_g": 1.0, "carbs_g": 5.9, "fat_g": 0.2, "fiber_g": 3.0, "sugar_g": 3.5, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-pumpkin-hokkaido", "name": "Kürbis (Hokkaido / Butternut)", "serving_size": 100, "calories_per_serving": 30, "protein_g": 1.2, "carbs_g": 6.5, "fat_g": 0.2, "fiber_g": 2.0, "sugar_g": 3.0, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-beetroot-cooked", "name": "Rote Bete (gekocht)", "serving_size": 100, "calories_per_serving": 44, "protein_g": 1.7, "carbs_g": 10.0, "fat_g": 0.2, "fiber_g": 2.0, "sugar_g": 8.0, "saturated_fat_g": 0.0, "sodium_mg": 78},
    {"id": "food-onion", "name": "Zwiebel", "serving_size": 100, "calories_per_serving": 40, "protein_g": 1.1, "carbs_g": 9.3, "fat_g": 0.1, "fiber_g": 1.7, "sugar_g": 4.2, "saturated_fat_g": 0.0, "sodium_mg": 4},
    {"id": "food-garlic", "name": "Knoblauch", "serving_size": 100, "calories_per_serving": 149, "protein_g": 6.4, "carbs_g": 33.1, "fat_g": 0.5, "fiber_g": 2.1, "sugar_g": 1.0, "saturated_fat_g": 0.1, "sodium_mg": 17},
    {"id": "food-mushrooms", "name": "Champignons (weiß / braun)", "serving_size": 100, "calories_per_serving": 22, "protein_g": 3.1, "carbs_g": 3.3, "fat_g": 0.3, "fiber_g": 1.0, "sugar_g": 2.0, "saturated_fat_g": 0.0, "sodium_mg": 5},
    {"id": "food-asparagus", "name": "Spargel (weiß / grün)", "serving_size": 100, "calories_per_serving": 20, "protein_g": 2.2, "carbs_g": 3.9, "fat_g": 0.1, "fiber_g": 2.1, "sugar_g": 1.9, "saturated_fat_g": 0.0, "sodium_mg": 2},
    {"id": "food-corn-canned", "name": "Mais / Zuckermais (Dose)", "serving_size": 100, "calories_per_serving": 80, "protein_g": 2.8, "carbs_g": 15.0, "fat_g": 1.2, "fiber_g": 2.4, "sugar_g": 4.5, "saturated_fat_g": 0.2, "sodium_mg": 180},
    {"id": "food-olives-green", "name": "Oliven (grün, entsteint)", "serving_size": 100, "calories_per_serving": 145, "protein_g": 1.0, "carbs_g": 3.8, "fat_g": 15.3, "fiber_g": 3.3, "sugar_g": 0.5, "saturated_fat_g": 2.0, "sodium_mg": 1550},

    # ══════════════════════════════════════════════════════════════════════
    # 🥜 NÜSSE, KERNE, SAMEN & ÖLE
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-almonds", "name": "Mandeln", "serving_size": 100, "calories_per_serving": 579, "protein_g": 21.2, "carbs_g": 21.6, "fat_g": 49.9, "fiber_g": 12.5, "sugar_g": 4.4, "saturated_fat_g": 3.8, "sodium_mg": 1},
    {"id": "food-walnuts", "name": "Walnüsse", "serving_size": 100, "calories_per_serving": 654, "protein_g": 15.2, "carbs_g": 13.7, "fat_g": 65.2, "fiber_g": 6.7, "sugar_g": 2.6, "saturated_fat_g": 6.1, "sodium_mg": 2},
    {"id": "food-hazelnuts", "name": "Haselnüsse", "serving_size": 100, "calories_per_serving": 628, "protein_g": 15.0, "carbs_g": 16.7, "fat_g": 60.8, "fiber_g": 9.7, "sugar_g": 4.3, "saturated_fat_g": 4.5, "sodium_mg": 0},
    {"id": "food-cashews", "name": "Cashewkerne", "serving_size": 100, "calories_per_serving": 553, "protein_g": 18.2, "carbs_g": 30.2, "fat_g": 43.8, "fiber_g": 3.3, "sugar_g": 5.9, "saturated_fat_g": 7.8, "sodium_mg": 12},
    {"id": "food-peanuts", "name": "Erdnüsse (geröstet, ungesalzen)", "serving_size": 100, "calories_per_serving": 585, "protein_g": 25.8, "carbs_g": 16.1, "fat_g": 49.2, "fiber_g": 8.5, "sugar_g": 4.7, "saturated_fat_g": 6.8, "sodium_mg": 18},
    {"id": "food-peanut-butter", "name": "Erdnussbutter / Erdnussmus (100%)", "serving_size": 100, "calories_per_serving": 588, "protein_g": 25.0, "carbs_g": 20.0, "fat_g": 50.0, "fiber_g": 6.0, "sugar_g": 6.0, "saturated_fat_g": 10.0, "sodium_mg": 15},
    {"id": "food-almond-butter", "name": "Mandelmus (100%)", "serving_size": 100, "calories_per_serving": 614, "protein_g": 21.0, "carbs_g": 10.0, "fat_g": 56.0, "fiber_g": 10.5, "sugar_g": 4.5, "saturated_fat_g": 4.5, "sodium_mg": 5},
    {"id": "food-tahini", "name": "Tahini / Sesammus", "serving_size": 100, "calories_per_serving": 595, "protein_g": 17.0, "carbs_g": 21.0, "fat_g": 54.0, "fiber_g": 9.3, "sugar_g": 0.5, "saturated_fat_g": 7.5, "sodium_mg": 115},
    {"id": "food-chia-seeds", "name": "Chiasamen", "serving_size": 100, "calories_per_serving": 486, "protein_g": 16.5, "carbs_g": 42.1, "fat_g": 30.7, "fiber_g": 34.4, "sugar_g": 0.8, "saturated_fat_g": 3.3, "sodium_mg": 16},
    {"id": "food-flaxseeds", "name": "Leinsamen (geschrotet)", "serving_size": 100, "calories_per_serving": 534, "protein_g": 18.3, "carbs_g": 28.9, "fat_g": 42.2, "fiber_g": 27.3, "sugar_g": 1.6, "saturated_fat_g": 3.7, "sodium_mg": 30},
    {"id": "food-pumpkin-seeds", "name": "Kürbiskerne", "serving_size": 100, "calories_per_serving": 559, "protein_g": 30.2, "carbs_g": 10.7, "fat_g": 49.1, "fiber_g": 6.0, "sugar_g": 1.4, "saturated_fat_g": 8.7, "sodium_mg": 7},
    {"id": "food-sunflower-seeds", "name": "Sonnenblumenkerne", "serving_size": 100, "calories_per_serving": 584, "protein_g": 20.8, "carbs_g": 20.0, "fat_g": 51.5, "fiber_g": 8.6, "sugar_g": 2.6, "saturated_fat_g": 4.5, "sodium_mg": 9},
    {"id": "food-olive-oil", "name": "Olivenöl (nativ extra)", "serving_size": 100, "calories_per_serving": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 14.0, "sodium_mg": 2},
    {"id": "food-rapeseed-oil", "name": "Rapsöl", "serving_size": 100, "calories_per_serving": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 7.0, "sodium_mg": 0},
    {"id": "food-linseed-oil", "name": "Leinöl", "serving_size": 100, "calories_per_serving": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 9.0, "sodium_mg": 0},
    {"id": "food-coconut-oil", "name": "Kokosöl / Kokosfett", "serving_size": 100, "calories_per_serving": 862, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 87.0, "sodium_mg": 0},

    # ══════════════════════════════════════════════════════════════════════
    # 🍯 SÜSSUNGSMITTEL, WÜRZMITTEL & SUPPLEMENTS
    # ══════════════════════════════════════════════════════════════════════
    {"id": "food-honey", "name": "Honig", "serving_size": 100, "calories_per_serving": 304, "protein_g": 0.3, "carbs_g": 82.4, "fat_g": 0.0, "fiber_g": 0.2, "sugar_g": 82.1, "saturated_fat_g": 0.0, "sodium_mg": 4},
    {"id": "food-maple-syrup", "name": "Ahornsirup", "serving_size": 100, "calories_per_serving": 260, "protein_g": 0.0, "carbs_g": 67.0, "fat_g": 0.1, "fiber_g": 0.0, "sugar_g": 60.5, "saturated_fat_g": 0.0, "sodium_mg": 12},
    {"id": "food-sugar", "name": "Haushaltszucker / Rohrzucker", "serving_size": 100, "calories_per_serving": 387, "protein_g": 0.0, "carbs_g": 100.0, "fat_g": 0.0, "fiber_g": 0.0, "sugar_g": 100.0, "saturated_fat_g": 0.0, "sodium_mg": 1},
    {"id": "food-erythritol", "name": "Erythrit (Süßungsmittel, 0 kcal)", "serving_size": 100, "calories_per_serving": 0, "protein_g": 0.0, "carbs_g": 100.0, "fat_g": 0.0, "fiber_g": 0.0, "sugar_g": 0.0, "saturated_fat_g": 0.0, "sodium_mg": 0},
    {"id": "food-dark-chocolate", "name": "Zartbitterschokolade (70% Kakao)", "serving_size": 100, "calories_per_serving": 598, "protein_g": 7.8, "carbs_g": 45.9, "fat_g": 42.6, "fiber_g": 10.9, "sugar_g": 24.0, "saturated_fat_g": 24.5, "sodium_mg": 20},
    {"id": "food-dark-chocolate-85", "name": "Zartbitterschokolade (85% Kakao)", "serving_size": 100, "calories_per_serving": 613, "protein_g": 8.5, "carbs_g": 19.0, "fat_g": 52.0, "fiber_g": 15.0, "sugar_g": 14.0, "saturated_fat_g": 31.0, "sodium_mg": 15},
    {"id": "food-cocoa-powder", "name": "Kakaopulver (schwach entölt)", "serving_size": 100, "calories_per_serving": 380, "protein_g": 20.0, "carbs_g": 15.0, "fat_g": 21.0, "fiber_g": 30.0, "sugar_g": 1.0, "saturated_fat_g": 12.5, "sodium_mg": 20},
    {"id": "food-whey-protein", "name": "Whey-Protein (Molkenprotein-Pulver)", "serving_size": 100, "calories_per_serving": 395, "protein_g": 78.0, "carbs_g": 6.5, "fat_g": 5.5, "fiber_g": 1.0, "sugar_g": 5.0, "saturated_fat_g": 3.0, "sodium_mg": 180},
    {"id": "food-casein-protein", "name": "Casein-Protein (Mizellares Kasein)", "serving_size": 100, "calories_per_serving": 370, "protein_g": 80.0, "carbs_g": 4.5, "fat_g": 2.0, "fiber_g": 0.5, "sugar_g": 3.5, "saturated_fat_g": 1.2, "sodium_mg": 150},
    {"id": "food-vegan-protein", "name": "Veganes Proteinpulver (Erbse/Reis)", "serving_size": 100, "calories_per_serving": 380, "protein_g": 75.0, "carbs_g": 7.0, "fat_g": 4.5, "fiber_g": 6.0, "sugar_g": 1.0, "saturated_fat_g": 1.0, "sodium_mg": 650},
    {"id": "food-soy-sauce", "name": "Sojasauce (Shoyu / Tamari)", "serving_size": 100, "calories_per_serving": 60, "protein_g": 10.5, "carbs_g": 5.0, "fat_g": 0.1, "fiber_g": 0.8, "sugar_g": 1.5, "saturated_fat_g": 0.0, "sodium_mg": 5600},
    {"id": "food-mustard", "name": "Senf (mittelscharf)", "serving_size": 100, "calories_per_serving": 90, "protein_g": 6.0, "carbs_g": 5.5, "fat_g": 5.0, "fiber_g": 3.5, "sugar_g": 2.0, "saturated_fat_g": 0.4, "sodium_mg": 1100},
    {"id": "food-tomato-paste", "name": "Tomatenmark (2-fach konzentriert)", "serving_size": 100, "calories_per_serving": 82, "protein_g": 4.5, "carbs_g": 15.0, "fat_g": 0.5, "fiber_g": 4.0, "sugar_g": 12.0, "saturated_fat_g": 0.1, "sodium_mg": 45},
    {"id": "food-hummus", "name": "Hummus", "serving_size": 100, "calories_per_serving": 177, "protein_g": 4.9, "carbs_g": 20.1, "fat_g": 8.6, "fiber_g": 4.0, "sugar_g": 0.3, "saturated_fat_g": 1.1, "sodium_mg": 380},
    {"id": "food-pesto-genovese", "name": "Pesto alla Genovese", "serving_size": 100, "calories_per_serving": 450, "protein_g": 5.0, "carbs_g": 6.0, "fat_g": 45.0, "fiber_g": 2.0, "sugar_g": 3.0, "saturated_fat_g": 7.0, "sodium_mg": 980},
]
