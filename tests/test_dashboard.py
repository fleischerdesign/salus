def test_dashboard_redirects_anonymous(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"


def test_dashboard_loads_authenticated(authenticated_client):
    response = authenticated_client.get("/")
    assert response.status_code == 200
    assert "salus" in response.text
