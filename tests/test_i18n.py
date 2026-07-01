def test_default_locale_en(authenticated_client):
    response = authenticated_client.get("/settings")
    assert response.status_code == 200
    assert "Account Settings" in response.text
    assert "Kontoeinstellungen" not in response.text


def test_accept_language_de(authenticated_client):
    # Pass Accept-Language header indicating German
    headers = {"Accept-Language": "de-DE,de;q=0.9"}
    response = authenticated_client.get("/settings", headers=headers)
    assert response.status_code == 200
    assert "Kontoeinstellungen" in response.text
    assert "Account Settings" not in response.text


def test_set_locale_cookie(authenticated_client):
    # Post locale selection
    response = authenticated_client.post(
        "/settings/locale",
        data={"locale": "de"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # The subsequent settings page should now be in German because cookie is set
    assert "Kontoeinstellungen" in response.text
    assert "Account Settings" not in response.text

    # Post back to English
    response = authenticated_client.post(
        "/settings/locale",
        data={"locale": "en"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Account Settings" in response.text
    assert "Kontoeinstellungen" not in response.text
