import uuid
from starlette.testclient import TestClient


def _push_cmd(client: TestClient, command: str, payload: dict) -> dict:
    resp = client.post("/api/v1/sync/push", json={"operations": [{"type": "command", "command": command, "payload": payload}]})
    assert resp.status_code == 200
    return resp.json()["results"][0]


def _push_create(client: TestClient, entity: str, data: dict) -> str:
    resp = client.post("/api/v1/sync/push", json={"operations": [{"type": "create", "entity": entity, "data": data}]})
    assert resp.status_code == 200
    result = resp.json()["results"][0]
    assert result["status"] == "created"
    return result["id"]


def _create_food_item(client: TestClient, name: str = "Oats") -> str:
    return _push_create(client, "food_item", {
        "name": name,
        "serving_size": 100.0,
        "calories_per_serving": 350.0,
        "protein_g": 12.0,
        "carbs_g": 60.0,
        "fat_g": 6.0,
    })


def _nutrition_measurements(client: TestClient) -> list[dict]:
    resp = client.get("/api/v1/measurements?metric_code=nutrition")
    assert resp.status_code == 200
    return resp.json()


class TestCreateMealHandler:
    def test_creates_meal_items_and_nutrition_bridge(self, authenticated_client: TestClient):
        food_id = _create_food_item(authenticated_client)
        measurement_id = str(uuid.uuid4())

        result = _push_cmd(authenticated_client, "create_meal", {
            "log_date": "2026-08-15",
            "meal_type": "lunch",
            "name": "Oat bowl",
            "measurement_id": measurement_id,
            "items": [{"food_item_id": food_id, "servings": 2}],
        })

        assert result["status"] == "created"
        meal_id = result["id"]

        meal = authenticated_client.get(f"/api/v1/meals/{meal_id}").json()
        assert len(meal["items"]) == 1
        assert meal["items"][0]["servings"] == 2
        assert meal["total_calories"] == 700.0

        measurements = _nutrition_measurements(authenticated_client)
        bridge = next((m for m in measurements if m["external_id"] == meal_id), None)
        assert bridge is not None
        assert bridge["source"] == "meal"
        assert '"calories": 700.0' in bridge["value_json"]

    def test_rejects_empty_meal(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "create_meal", {"items": []})
        assert result["status"] == "error"

    def test_delete_removes_items_and_measurement(self, authenticated_client: TestClient):
        food_id = _create_food_item(authenticated_client)
        created = _push_cmd(authenticated_client, "create_meal", {
            "items": [{"food_item_id": food_id, "servings": 1}],
        })
        meal_id = created["id"]
        assert _nutrition_measurements(authenticated_client)

        deleted = _push_cmd(authenticated_client, "delete_meal", {"id": meal_id})
        assert deleted["status"] == "deleted"

        measurements = _nutrition_measurements(authenticated_client)
        assert not any(m["external_id"] == meal_id for m in measurements)


class TestRecipeCommands:
    def test_create_recipe_writes_ingredients(self, authenticated_client: TestClient):
        food_id = _create_food_item(authenticated_client)
        result = _push_cmd(authenticated_client, "create_recipe", {
            "name": "Porridge",
            "servings": 2,
            "ingredients": [{"food_item_id": food_id, "amount_g": 150.0}],
        })
        assert result["status"] == "created"
        recipe_id = result["id"]

        recipe = authenticated_client.get(f"/api/v1/recipes/{recipe_id}").json()
        assert len(recipe["ingredients"]) == 1
        assert recipe["ingredients"][0]["amount_g"] == 150.0

    def test_cook_recipe_creates_meal_and_nutrition_bridge(
        self, authenticated_client: TestClient
    ):
        food_id = _create_food_item(authenticated_client)
        created = _push_cmd(authenticated_client, "create_recipe", {
            "name": "Porridge",
            "servings": 2,
            "ingredients": [{"food_item_id": food_id, "amount_g": 100.0}],
        })
        recipe_id = created["id"]

        result = _push_cmd(authenticated_client, "cook_recipe", {"recipe_id": recipe_id})
        assert result["status"] == "created"
        meal_id = result["id"]

        meal = authenticated_client.get(f"/api/v1/meals/{meal_id}").json()
        assert len(meal["items"]) == 1
        measurements = _nutrition_measurements(authenticated_client)
        assert any(m["external_id"] == meal_id and m["source"] == "meal" for m in measurements)


class TestToggleHabitCheckHandler:
    def test_toggles_today_log(self, authenticated_client: TestClient):
        habit_id = _push_create(authenticated_client, "habit", {
            "name": "Read", "frequency": "daily", "color": "#fff", "icon": "book",
        })

        checked = _push_cmd(authenticated_client, "toggle_habit_check", {"habit_id": habit_id})
        assert checked["status"] == "created"
        assert checked["extra"]["completed"] is True

        unchecked = _push_cmd(authenticated_client, "toggle_habit_check", {"habit_id": habit_id})
        assert unchecked["status"] == "updated"
        assert unchecked["extra"]["completed"] is False

    def test_unknown_habit(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "toggle_habit_check", {"habit_id": str(uuid.uuid4())})
        assert result["status"] == "not_found"


class TestMedicationCommands:
    def test_log_and_skip(self, authenticated_client: TestClient):
        medication_id = _push_create(authenticated_client, "medication", {"name": "Metformin"})

        logged = _push_cmd(authenticated_client, "log_medication", {"medication_id": medication_id})
        assert logged["status"] == "created"
        assert logged["record"]["skipped"] is False

        skipped = _push_cmd(authenticated_client, "skip_medication_dose", {
            "medication_id": medication_id,
            "schedule_id": "schedule-1",
            "scheduled_time": "08:00",
        })
        assert skipped["status"] == "created"
        assert skipped["record"]["skipped"] is True
