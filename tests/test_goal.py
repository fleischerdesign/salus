from salus.models.goal import GoalDirection, GoalFrequency, NutritionField
from salus.models.measurement import Measurement
from salus.services.analytics.calculations import compute_goal_progress
from salus.services.goal import _extract_current_value


def _get_metric_code(client, name: str) -> str:
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    for m in resp.json():
        if m["name"] == name:
            return m["id"]
    raise ValueError(f"Metric {name} not found")


class TestComputeGoalProgress:
    def test_no_current_value_returns_pending(self):
        pct, status, fulfilled = compute_goal_progress(
            None, 100, GoalDirection.INCREASE, GoalFrequency.DAILY
        )
        assert pct == 0
        assert status == "pending"
        assert not fulfilled

    def test_increase_fulfilled(self):
        pct, status, fulfilled = compute_goal_progress(
            120, 100, GoalDirection.INCREASE, GoalFrequency.DAILY
        )
        assert pct == 100
        assert status == "fulfilled"
        assert fulfilled

    def test_increase_partial(self):
        pct, status, fulfilled = compute_goal_progress(
            75, 100, GoalDirection.INCREASE, GoalFrequency.DAILY
        )
        assert pct == 75
        assert status == "pending"
        assert not fulfilled

    def test_decrease_fulfilled(self):
        pct, status, fulfilled = compute_goal_progress(
            78, 80, GoalDirection.DECREASE, GoalFrequency.ONCE
        )
        assert pct == 100
        assert status == "fulfilled"
        assert fulfilled

    def test_decrease_partial(self):
        pct, status, fulfilled = compute_goal_progress(
            85, 80, GoalDirection.DECREASE, GoalFrequency.ONCE
        )
        assert 90 <= pct < 100
        assert status == "pending"
        assert not fulfilled

    def test_once_missed_deadline(self):
        pct, status, fulfilled = compute_goal_progress(
            85, 80, GoalDirection.DECREASE, GoalFrequency.ONCE, deadline_passed=True
        )
        assert status == "missed"
        assert not fulfilled

    def test_once_fulfilled_before_deadline(self):
        pct, status, fulfilled = compute_goal_progress(
            78, 80, GoalDirection.DECREASE, GoalFrequency.ONCE, deadline_passed=True
        )
        assert status == "fulfilled"
        assert fulfilled


class TestNutritionGoalEvaluation:
    def _measurement(self, value_json: dict) -> Measurement:
        import json

        return Measurement(
            id="x",
            user_id="u",
            metric_code="nutrition",
            value_numeric=None,
            value_json=json.dumps(value_json),
        )

    def test_protein_sum_over_multiple_meals(self):
        entries = [
            self._measurement({"calories": 400, "protein_grams": 30}),
            self._measurement({"calories": 600, "protein_grams": 45}),
        ]
        current = _extract_current_value(
            entries, GoalDirection.INCREASE, "nutrition", NutritionField.PROTEIN
        )
        assert current == 75

    def test_calories_sum_with_legacy_key_fallback(self):
        entries = [
            self._measurement({"total_kcal": 420}),
            self._measurement({"total_kcal": 180}),
        ]
        current = _extract_current_value(
            entries, GoalDirection.INCREASE, "nutrition", NutritionField.CALORIES
        )
        assert current == 600

    def test_skips_rows_without_sub_field(self):
        entries = [
            self._measurement({"calories": 500, "protein_grams": 20}),
            self._measurement({"calories": 300}),  # no protein key
        ]
        current = _extract_current_value(
            entries, GoalDirection.DECREASE, "nutrition", NutritionField.PROTEIN
        )
        assert current == 20

    def test_invalid_json_is_ignored(self):
        entries = [Measurement(id="x", user_id="u", metric_code="nutrition", value_json="not-json")]
        current = _extract_current_value(
            entries, GoalDirection.INCREASE, "nutrition", NutritionField.CARBS
        )
        assert current == 0

    def test_non_nutrition_metric_unaffected(self):
        entries = [self._measurement({"calories": 500})]
        current = _extract_current_value(
            entries, GoalDirection.INCREASE, "steps", None
        )
        assert current is None


class TestGoalRoutes:
    def test_goals_requires_auth(self, client):
        response = client.get("/api/v1/goals", follow_redirects=False)
        assert response.status_code in (401, 403)

    def test_goals_list_empty(self, authenticated_client):
        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_and_list_goal(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_code": "steps",
                "target_value": 10000,
                "direction": "increase",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["metric_code"] == "steps"
        assert data["target_value"] == 10000

        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        goals = response.json()
        assert len(goals) == 1
        assert goals[0]["metric_code"] == "steps"

    def test_create_goal_with_entry_does_not_error(self, authenticated_client):
        weight_code = _get_metric_code(authenticated_client, "Weight")
        authenticated_client.post(
            "/api/v1/measurements",
            json={"metric_code": weight_code, "value_text": "80.5"},
        )
        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_code": "weight",
                "target_value": 75,
                "direction": "decrease",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201

    def test_goal_user_scoped(self, authenticated_client, client):
        weight_code = _get_metric_code(authenticated_client, "Weight")
        authenticated_client.post(
            "/api/v1/measurements",
            json={"metric_code": weight_code, "value_text": "70"},
        )
        authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_code": "weight",
                "target_value": 65,
                "direction": "decrease",
                "frequency": "daily",
            },
        )

        client.post("/api/v1/auth/logout")
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "bob", "password": "secret456"},
        )
        bob_token = resp.json()["token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}

        bob_weight_code = _get_metric_code(client, "Weight")
        client.post(
            "/api/v1/measurements",
            json={"metric_code": bob_weight_code, "value_text": "90"},
            headers=bob_headers,
        )

        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_create_goal_no_data(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_code": "weight",
                "target_value": 10000,
                "direction": "increase",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201

    def test_delete_goal(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_code": "weight",
                "target_value": 10000,
                "direction": "increase",
                "frequency": "daily",
            },
        )
        goal_id = resp.json()["id"]
        response = authenticated_client.delete(f"/api/v1/goals/{goal_id}")
        assert response.status_code == 204

        response = authenticated_client.get("/api/v1/goals")
        assert response.json() == []
