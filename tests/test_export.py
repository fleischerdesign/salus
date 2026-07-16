import json


class TestExportService:
    def test_csv_download(self, authenticated_client):
        authenticated_client.post(
            "/api/v1/entries?metric_code=weight",
            json={"value": "80.5"},
        )
        response = authenticated_client.get("/export/download?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        content = response.content.decode()
        assert "80.5" in content

    def test_json_download(self, authenticated_client):
        authenticated_client.post(
            "/api/v1/entries?metric_code=weight",
            json={"value": "80.5"},
        )
        response = authenticated_client.get("/export/download?format=json")
        assert response.status_code == 200
        data = json.loads(response.content.decode())
        assert isinstance(data, list)
        assert len(data) >= 1
