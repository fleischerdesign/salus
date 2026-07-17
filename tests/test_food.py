class TestFoodItemRoutes:
    def test_list_empty_search(self, client):
        resp = client.get("/api/v1/food/items/search?q=notfound")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_create_and_search(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/food/items", json={
            "name": "Haferflocken",
            "brand": "Alnatura",
            "calories_per_serving": 370,
            "protein_g": 13.0,
            "carbs_g": 59.0,
            "fat_g": 7.0,
            "serving_size": 100,
            "serving_unit": "g",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Haferflocken"
        assert data["calories_per_serving"] == 370.0

        resp = authenticated_client.get("/api/v1/food/items/search?q=Hafer")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    def test_get_food_item(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/food/items", json={
            "name": "Bananen",
            "calories_per_serving": 89,
            "protein_g": 1.1,
            "carbs_g": 22.8,
            "fat_g": 0.3,
        })
        item_id = resp.json()["id"]

        resp = authenticated_client.get(f"/api/v1/food/items/{item_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Bananen"

    def test_barcode(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/food/items", json={
            "name": "Item With Barcode",
            "barcode": "1234567890123",
            "calories_per_serving": 100,
            "protein_g": 5.0,
            "carbs_g": 10.0,
            "fat_g": 2.0,
        })
        item_id = resp.json()["id"]

        resp = authenticated_client.get("/api/v1/food/items/barcode/1234567890123")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Item With Barcode"

        resp = authenticated_client.get("/api/v1/food/items/barcode/doesnotexist")
        assert resp.json() is None


class TestMealRoutes:
    def test_create_and_get_meal(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/food/items", json={
            "name": "Test Food",
            "calories_per_serving": 100,
            "protein_g": 10.0,
            "carbs_g": 20.0,
            "fat_g": 5.0,
        })
        food_id = resp.json()["id"]

        resp = authenticated_client.post("/api/v1/meals", json={
            "meal_type": "lunch",
            "name": "Test Lunch",
            "items": [
                {"food_item_id": food_id, "servings": 2}
            ],
        })
        assert resp.status_code == 201
        meal = resp.json()
        assert meal["meal_type"] == "lunch"
        assert len(meal["items"]) == 1
        assert meal["items"][0]["food_item_name"] == "Test Food"
        assert meal["total_calories"] == 200.0
        assert meal["total_protein_g"] == 20.0
        assert meal["total_carbs_g"] == 40.0
        assert meal["total_fat_g"] == 10.0

    def test_get_today(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/meals/today")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_summary(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/meals/summary")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_delete_meal(self, authenticated_client):
        food = authenticated_client.post("/api/v1/food/items", json={
            "name": "Delete Test",
            "calories_per_serving": 50,
            "protein_g": 3.0,
            "carbs_g": 7.0,
            "fat_g": 1.0,
        })
        food_id = food.json()["id"]

        meal = authenticated_client.post("/api/v1/meals", json={
            "items": [{"food_item_id": food_id, "servings": 1}],
        })
        meal_id = meal.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/meals/{meal_id}")
        assert resp.status_code == 204

    def test_empty_meal_rejected(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/meals", json={
            "items": [],
        })
        assert resp.status_code == 400

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/meals")
        assert resp.status_code == 401

    def test_cannot_access_other_user_meal(self, authenticated_client):
        food = authenticated_client.post("/api/v1/food/items", json={
            "name": "Shared Food",
            "calories_per_serving": 100,
            "protein_g": 5.0,
            "carbs_g": 10.0,
            "fat_g": 2.0,
        })
        food_id = food.json()["id"]

        meal = authenticated_client.post("/api/v1/meals", json={
            "items": [{"food_item_id": food_id, "servings": 1}],
        })
        meal_id = meal.json()["id"]

        headers = authenticated_client.headers
        try:
            authenticated_client.headers = {}
            reg = authenticated_client.post("/api/v1/auth/register", json={
                "username": "meal_other",
                "password": "secret123",
                "email": "meal_other@salus.local",
                "display_name": "Other",
            })
            other_token = reg.json().get("token", "")
            authenticated_client.headers = {"Authorization": f"Bearer {other_token}"}
            resp = authenticated_client.get(f"/api/v1/meals/{meal_id}")
            assert resp.status_code == 404
        finally:
            authenticated_client.headers = headers


class TestRecipeRoutes:
    def test_create_and_get_recipe(self, authenticated_client):
        food = authenticated_client.post("/api/v1/food/items", json={
            "name": "Recipe Ingredient",
            "calories_per_serving": 100,
            "protein_g": 10.0,
            "carbs_g": 20.0,
            "fat_g": 5.0,
            "serving_size": 100,
        })
        food_id = food.json()["id"]

        recipe = authenticated_client.post("/api/v1/recipes", json={
            "name": "Test Recipe",
            "description": "A test",
            "servings": 2,
            "prep_time_min": 10,
            "cook_time_min": 20,
            "ingredients": [
                {"food_item_id": food_id, "amount_g": 200}
            ],
        })
        assert recipe.status_code == 201
        data = recipe.json()
        assert data["name"] == "Test Recipe"
        assert data["servings"] == 2
        assert len(data["ingredients"]) == 1
        assert data["total_calories"] == 200.0

    def test_list_recipes(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/recipes")
        assert resp.status_code == 200

    def test_delete_recipe(self, authenticated_client):
        food = authenticated_client.post("/api/v1/food/items", json={
            "name": "Del Recipe Ing",
            "calories_per_serving": 50,
            "protein_g": 2.0,
            "carbs_g": 5.0,
            "fat_g": 1.0,
        })
        food_id = food.json()["id"]

        recipe = authenticated_client.post("/api/v1/recipes", json={
            "name": "To Delete",
            "servings": 1,
            "ingredients": [{"food_item_id": food_id, "amount_g": 50}],
        })
        recipe_id = recipe.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/recipes/{recipe_id}")
        assert resp.status_code == 204

    def test_cook_recipe(self, authenticated_client):
        food = authenticated_client.post("/api/v1/food/items", json={
            "name": "Cook Ingredient",
            "calories_per_serving": 100,
            "protein_g": 10.0,
            "carbs_g": 20.0,
            "fat_g": 5.0,
            "serving_size": 100,
        })
        food_id = food.json()["id"]

        recipe = authenticated_client.post("/api/v1/recipes", json={
            "name": "To Cook",
            "servings": 2,
            "ingredients": [{"food_item_id": food_id, "amount_g": 200}],
        })
        recipe_id = recipe.json()["id"]

        resp = authenticated_client.post(f"/api/v1/recipes/{recipe_id}/cook")
        assert resp.status_code == 200
        meal = resp.json()
        assert "Recipe: To Cook" in meal["name"]
        assert meal["total_calories"] > 0

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/recipes")
        assert resp.status_code == 401
