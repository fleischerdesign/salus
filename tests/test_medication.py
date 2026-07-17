class TestMedicationRoutes:
    def test_list_empty(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/medications")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Ibuprofen 400",
            "active_ingredient": "Ibuprofen",
            "strength": "400mg",
            "form": "tablet",
            "instructions": "Mit Mahlzeit einnehmen",
            "color_hex": "#ef4444",
            "icon": "pill",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Ibuprofen 400"
        assert data["is_active"] is True

        resp = authenticated_client.get("/api/v1/medications")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_medication(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Metformin",
            "strength": "500mg",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Metformin"

    def test_update_medication(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Old Name",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.put(f"/api/v1/medications/{med_id}", json={
            "name": "New Name",
            "strength": "100mg",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["strength"] == "100mg"

    def test_delete_medication(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "To Delete",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/medications/{med_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}")
        assert resp.status_code == 404

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/medications")
        assert resp.status_code == 401

    def test_cannot_access_other_user_medication(self, authenticated_client):
        headers = authenticated_client.headers
        try:
            resp = authenticated_client.post("/api/v1/medications", json={
                "name": "Mine",
            })
            med_id = resp.json()["id"]

            authenticated_client.headers = {}
            reg = authenticated_client.post("/api/v1/auth/register", json={
                "username": "med_other_user",
                "password": "secret123",
                "email": "med_other@salus.local",
                "display_name": "Other",
            })
            other_token = reg.json().get("token", "")

            authenticated_client.headers = {"Authorization": f"Bearer {other_token}"}
            resp = authenticated_client.get(f"/api/v1/medications/{med_id}")
            assert resp.status_code == 404
        finally:
            authenticated_client.headers = headers

    def test_add_and_get_schedule(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Scheduled Med",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.post(f"/api/v1/medications/{med_id}/schedule", json={
            "dosage": "1 Tablette",
            "times": ["08:00", "20:00"],
            "days_of_week": [1, 2, 3, 4, 5],
            "start_date": "2026-01-01",
        })
        assert resp.status_code == 201
        sched = resp.json()
        assert sched["dosage"] == "1 Tablette"
        assert sched["times"] == ["08:00", "20:00"]
        assert sched["days_of_week"] == [1, 2, 3, 4, 5]

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}/schedule")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_delete_schedule(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "With Schedule",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.post(f"/api/v1/medications/{med_id}/schedule", json={
            "dosage": "1 Tablette",
            "times": ["08:00"],
        })
        sched_id = resp.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/medications/schedule/{sched_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}/schedule")
        assert resp.json() == []

    def test_log_intake(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Logged Med",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.post(f"/api/v1/medications/{med_id}/log", json={
            "taken_at": "2026-07-15T08:00:00",
            "dosage_taken": "1 Tablette",
            "skipped": False,
        })
        assert resp.status_code == 201
        log = resp.json()
        assert log["skipped"] is False
        assert log["dosage_taken"] == "1 Tablette"

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}/log")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_today(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Today Med",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.post(f"/api/v1/medications/{med_id}/schedule", json={
            "dosage": "1 Tablette",
            "times": ["08:00", "20:00"],
            "start_date": "2026-01-01",
        })

        resp = authenticated_client.get("/api/v1/medications/today")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "as_needed" in data

    def test_inventory(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Inventory Med",
        })
        med_id = resp.json()["id"]

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}/inventory")
        assert resp.status_code == 204

        resp = authenticated_client.put(f"/api/v1/medications/{med_id}/inventory", json={
            "initial_count": 100,
            "remaining_count": 80,
            "refill_at_count": 10,
        })
        assert resp.status_code == 200
        inv = resp.json()
        assert inv["initial_count"] == 100
        assert inv["remaining_count"] == 80
        assert inv["needs_refill"] is False

    def test_inventory_refill_warning(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "Low Med",
        })
        med_id = resp.json()["id"]

        authenticated_client.put(f"/api/v1/medications/{med_id}/inventory", json={
            "initial_count": 100,
            "remaining_count": 5,
            "refill_at_count": 10,
        })

        resp = authenticated_client.get(f"/api/v1/medications/{med_id}/inventory")
        assert resp.status_code == 200
        assert resp.json()["needs_refill"] is True

    def test_as_needed_in_today(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/medications", json={
            "name": "As Needed Med",
            "instructions": "Bei Bedarf",
        })

        resp = authenticated_client.get("/api/v1/medications/today")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["as_needed"]) >= 1
        assert any(m["name"] == "As Needed Med" for m in data["as_needed"])
