from datetime import datetime, timezone

from salus.models.goal import GoalDirection, GoalFrequency
from salus.services.analytics.calculations import compute_goal_progress


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
    def test_goals_redirects_anonymous(self, client):
        response = client.get("/goals", follow_redirects=False)
        assert response.status_code in (303, 302)

    def test_goals_page_loads_authenticated(self, authenticated_client):
        authenticated_client.post(
            "/entries/metric",
            data={"name": "CustomWeight", "unit": "kg", "data_type": "number"},
            follow_redirects=True,
        )
        response = authenticated_client.get("/goals")
        assert response.status_code == 200
        assert "Active Goals" in response.text

    def test_create_goal(self, authenticated_client):
        authenticated_client.post(
            "/entries/metric",
            data={"name": "CustomSteps", "unit": "steps", "data_type": "number"},
            follow_redirects=True,
        )
        response = authenticated_client.post("/goals", data={
            "metric_type_id": "13",
            "target_value": 10000,
            "direction": "increase",
            "frequency": "daily",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert "fulfilled" in response.text or "pending" in response.text

    def test_goal_progress_with_data_on_pre_seeded_metric(self, authenticated_client):
        authenticated_client.post("/entries", data={
            "value": "80.5",
            "metric_type_id": "4",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, follow_redirects=True)
        authenticated_client.post("/goals", data={
            "metric_type_id": "4",
            "target_value": "75",
            "direction": "decrease",
            "frequency": "daily",
        }, follow_redirects=True)
        response = authenticated_client.get("/goals")
        assert response.status_code == 200
        assert "80.5" in response.text or "8005" in response.text
        assert "pending" in response.text

    def test_goal_progress_user_scoped(self, authenticated_client, client):
        authenticated_client.post("/entries", data={
            "value": "70",
            "metric_type_id": "4",
        }, follow_redirects=True)
        authenticated_client.post("/goals", data={
            "metric_type_id": "4",
            "target_value": "65",
            "direction": "decrease",
            "frequency": "daily",
        }, follow_redirects=True)

        client.post("/auth/logout", follow_redirects=True)
        client.post("/auth/register", data={
            "username": "bob", "password": "secret456",
        }, follow_redirects=True)
        client.post("/entries", data={
            "value": "90",
            "metric_type_id": "16",
        }, follow_redirects=True)

        response = authenticated_client.get("/goals")
        assert response.status_code == 200
        assert "90" not in response.text

    def test_goal_progress_no_data_shows_pending(self, authenticated_client):
        authenticated_client.post("/goals", data={
            "metric_type_id": "4",
            "target_value": "10000",
            "direction": "increase",
            "frequency": "daily",
        }, follow_redirects=True)
        response = authenticated_client.get("/goals")
        assert response.status_code == 200
        assert "pending" in response.text
