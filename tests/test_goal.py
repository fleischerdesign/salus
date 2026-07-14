from salus.models.goal import GoalDirection, GoalFrequency
from salus.services.analytics.calculations import compute_goal_progress


def _get_metric_id(client, name: str) -> str:
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    for mt in resp.json():
        if mt["name"] == name:
            return mt["id"]
    raise ValueError(f"Metric type {name} not found")


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


class TestGoalRoutes:
    def test_goals_requires_auth(self, client):
        response = client.get("/api/v1/goals", follow_redirects=False)
        assert response.status_code in (401, 403)

    def test_goals_list_empty(self, authenticated_client):
        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_and_list_goal(self, authenticated_client):
        resp = authenticated_client.post(
            "/api/v1/metrics",
            json={"name": "CustomSteps", "unit": "steps", "data_type": "number"},
        )
        metric_id = resp.json()["id"]

        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_type_id": metric_id,
                "target_value": 10000,
                "direction": "increase",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["metric_type_id"] == metric_id
        assert data["target_value"] == 10000

        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        goals = response.json()
        assert len(goals) == 1
        assert goals[0]["metric_type_id"] == metric_id

    def test_create_goal_with_entry_does_not_error(self, authenticated_client):
        weight_id = _get_metric_id(authenticated_client, "Weight")
        authenticated_client.post(
            f"/api/v1/entries?metric_type_id={weight_id}",
            json={"value": "80.5"},
        )
        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_type_id": weight_id,
                "target_value": 75,
                "direction": "decrease",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201

    def test_goal_user_scoped(self, authenticated_client, client):
        weight_id = _get_metric_id(authenticated_client, "Weight")
        authenticated_client.post(
            f"/api/v1/entries?metric_type_id={weight_id}",
            json={"value": "70"},
        )
        authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_type_id": weight_id,
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

        # Bob needs to resolve Weight ID too
        bob_weight_id = _get_metric_id(client, "Weight")
        client.post(
            f"/api/v1/entries?metric_type_id={bob_weight_id}",
            json={"value": "90"},
            headers=bob_headers,
        )

        response = authenticated_client.get("/api/v1/goals")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_create_goal_no_data(self, authenticated_client):
        weight_id = _get_metric_id(authenticated_client, "Weight")
        response = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_type_id": weight_id,
                "target_value": 10000,
                "direction": "increase",
                "frequency": "daily",
            },
        )
        assert response.status_code == 201

    def test_delete_goal(self, authenticated_client):
        weight_id = _get_metric_id(authenticated_client, "Weight")
        resp = authenticated_client.post(
            "/api/v1/goals",
            json={
                "metric_type_id": weight_id,
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
