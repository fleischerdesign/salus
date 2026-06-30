def test_dashboard_shows_onboarding_modal_after_register(client):
    client.post(
        "/auth/register",
        data={"username": "newuser", "password": "secret789"},
        follow_redirects=True,
    )
    response = client.get("/")
    assert response.status_code == 200
    assert "Connect a Data Source" in response.text
    assert "Log Your First Entry" in response.text
    assert "Set Your First Goal" in response.text
    assert "onboarding-overlay" in response.text
    assert "Getting Started" in response.text


def test_dashboard_shows_card_after_modal_closed(client):
    client.post(
        "/auth/register",
        data={"username": "carduser", "password": "secret789"},
        follow_redirects=True,
    )
    response = client.get("/", cookies={"onboarding_modal_closed": "1"})
    assert response.status_code == 200
    assert "Getting Started" in response.text
    assert "onboarding-overlay" not in response.text


def test_dismiss_onboarding_hides_both(authenticated_client):
    response = authenticated_client.post("/onboarding/dismiss")
    assert response.status_code == 200

    response = authenticated_client.get("/")
    assert "Connect a Data Source" not in response.text
    assert "Getting Started" not in response.text


def test_dashboard_hides_onboarding_after_login_and_dismiss(authenticated_client):
    response = authenticated_client.get("/")
    assert "Connect a Data Source" in response.text

    authenticated_client.post("/onboarding/dismiss")
    response = authenticated_client.get("/")
    assert "Connect a Data Source" not in response.text
    assert "Getting Started" not in response.text


def test_onboarding_create_token_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/onboarding/token",
        data={"label": "Test Token"},
    )
    assert response.status_code == 200
    assert "onboarding-success" in response.text


def test_onboarding_create_entry_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/onboarding/entry",
        data={"metric_type_id": 1, "value": "42"},
    )
    assert response.status_code == 200
    assert "onboarding-success" in response.text


def test_onboarding_create_goal_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/onboarding/goal",
        data={"metric_type_id": 1, "target_value": "100", "direction": "increase"},
    )
    assert response.status_code == 200
    assert "onboarding-success" in response.text


def test_onboarding_requires_auth(client):
    response = client.post("/onboarding/dismiss", follow_redirects=False)
    assert response.status_code in (303, 302)


def test_onboarding_token_requires_auth(client):
    response = client.post("/onboarding/token", data={"label": "X"}, follow_redirects=False)
    assert response.status_code in (303, 302)


def test_onboarding_entry_requires_auth(client):
    response = client.post("/onboarding/entry", data={"metric_type_id": 1, "value": "1"}, follow_redirects=False)
    assert response.status_code in (303, 302)


def test_onboarding_goal_requires_auth(client):
    response = client.post("/onboarding/goal", data={"metric_type_id": 1, "target_value": "1"}, follow_redirects=False)
    assert response.status_code in (303, 302)


def test_onboarding_step_modal_token(authenticated_client):
    response = authenticated_client.get("/onboarding/step/0/modal")
    assert response.status_code == 200
    assert "Generate Token" in response.text
    assert "modal-close" in response.text


def test_onboarding_step_modal_entry(authenticated_client):
    response = authenticated_client.get("/onboarding/step/1/modal")
    assert response.status_code == 200
    assert "Log Entry" in response.text


def test_onboarding_step_modal_goal(authenticated_client):
    response = authenticated_client.get("/onboarding/step/2/modal")
    assert response.status_code == 200
    assert "Create Goal" in response.text


def test_onboarding_step_modal_invalid_n(authenticated_client):
    response = authenticated_client.get("/onboarding/step/9/modal")
    assert response.status_code == 404


def test_onboarding_step_modal_requires_auth(client):
    response = client.get("/onboarding/step/0/modal", follow_redirects=False)
    assert response.status_code in (303, 302)
