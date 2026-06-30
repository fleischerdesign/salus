def test_dashboard_redirects_anonymous(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"


def test_dashboard_loads_authenticated(authenticated_client):
    response = authenticated_client.get("/")
    assert response.status_code == 200
    assert "salus" in response.text


def test_dashboard_shows_day_navigator(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    response = client.get("/")
    assert response.status_code == 200
    assert "day-navigator" in response.text
    assert "chevron_left" in response.text


def test_dashboard_grid_htmx_endpoint(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    response = client.get("/dashboard/grid")
    assert response.status_code == 200
    assert "day-navigator" in response.text
    assert "dashboard-grid" in response.text


def test_dashboard_grid_with_date(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    response = client.get("/dashboard/grid?date=2024-01-15")
    assert response.status_code == 200
    assert "Jan 15" in response.text


def test_dashboard_grid_requires_auth(client):
    response = client.get("/dashboard/grid", follow_redirects=False)
    assert response.status_code == 303
    assert "/auth/login" in response.headers["location"]


def test_dashboard_today_button_not_visible_when_on_today(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    response = client.get("/dashboard/grid")
    assert response.status_code == 200
    assert 'class="btn-sm"' not in response.text


def test_dashboard_today_button_visible_for_past_date(client):
    client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=True,
    )
    response = client.get("/dashboard/grid?date=2024-01-15")
    assert response.status_code == 200
    assert "Today" in response.text
