import pytest

from salus.services.parser import (
    FlexiblePayloadParser,
    FlatArrayParser,
    HealthConnectWebhookParser,
)


class TestHealthConnectWebhookParser:
    def test_parses_standard_payload(self):
        payload = {
            "steps": [
                {"count": 8500, "start_time": "2026-06-24T08:00:00", "end_time": "2026-06-24T22:00:00"}
            ],
        }
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert len(records) == 1
        assert records[0].data_type == "steps"
        assert records[0].source == "samsung_health"
        assert "8500" in records[0].value_json

    def test_generates_external_id(self):
        payload = {
            "steps": [
                {"count": 100, "start_time": "2026-01-01T12:00:00", "end_time": "2026-01-01T13:00:00"}
            ],
        }
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert len(records) == 1
        assert len(records[0].external_id) == 32

    def test_uses_native_id_if_present(self):
        payload = {
            "steps": [
                {"id": "abc-123", "count": 100, "start_time": "2026-01-01T12:00:00"}
            ],
        }
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert records[0].external_id == "abc-123"

    def test_skips_metadata_keys(self):
        payload = {"timestamp": "2026-06-24T14:48:45Z", "app_version": "1.0.0"}
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert len(records) == 0

    def test_skips_non_list_data_type(self):
        payload = {"steps": "not_a_list"}
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert len(records) == 0

    def test_multiple_data_types(self):
        payload = {
            "steps": [{"count": 5000, "start_time": "2026-01-01T08:00:00"}],
            "heart_rate": [{"bpm": 72, "start_time": "2026-01-01T08:00:00"}],
            "weight": [{"weight_kg": 80.5, "start_time": "2026-01-01T08:00:00"}],
        }
        parser = HealthConnectWebhookParser()
        records = parser.parse(payload)
        assert len(records) == 3


class TestFlatArrayParser:
    def test_parses_flat_array(self):
        payload = [
            {"id": "1", "type": "steps", "startTime": "2026-01-01T08:00:00",
             "endTime": "2026-01-01T09:00:00", "value": {"count": 5000}},
        ]
        parser = FlatArrayParser()
        records = parser.parse(payload)
        assert len(records) == 1
        assert records[0].data_type == "steps"
        assert records[0].external_id == "1"
        assert "5000" in records[0].value_json

    def test_generates_external_id_when_missing(self):
        payload = [
            {"type": "steps", "startTime": "2026-01-01T08:00:00", "value": {"count": 5000}},
        ]
        parser = FlatArrayParser()
        records = parser.parse(payload)
        assert len(records) == 1
        assert len(records[0].external_id) == 32


class TestFlexiblePayloadParser:
    def setup_method(self):
        self.parser = FlexiblePayloadParser()

    def test_detects_health_connect_format(self):
        payload = {"steps": [{"count": 5000, "start_time": "2026-01-01T08:00:00"}]}
        records = self.parser.parse(payload)
        assert len(records) == 1

    def test_detects_flat_array_format(self):
        payload = [{"id": "1", "type": "steps", "startTime": "2026-01-01T08:00:00", "value": {"count": 5000}}]
        records = self.parser.parse(payload)
        assert len(records) == 1

    def test_detects_wrapped_records(self):
        payload = {"records": [{"id": "1", "type": "steps", "startTime": "2026-01-01T08:00:00", "value": {"count": 5000}}]}
        records = self.parser.parse(payload)
        assert len(records) == 1

    def test_detects_wrapped_data(self):
        payload = {"data": [{"id": "1", "type": "steps", "startTime": "2026-01-01T08:00:00", "value": {"count": 5000}}]}
        records = self.parser.parse(payload)
        assert len(records) == 1

    def test_detects_single_record(self):
        payload = {"id": "1", "type": "steps", "startTime": "2026-01-01T08:00:00", "value": {"count": 5000}}
        records = self.parser.parse(payload)
        assert len(records) == 1

    def test_raises_on_unknown_format(self):
        payload = {"something": "unexpected", "another": 42}
        with pytest.raises(ValueError):
            self.parser.parse(payload)
