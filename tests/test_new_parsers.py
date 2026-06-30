from salus.services.parser import (
    FlexiblePayloadParser,
    FlatArrayParser,
    HealthConnectWebhookParser,
)
from salus.services.parsers.apple_health import AppleHealthExportParser
from salus.services.parsers.fitbit import FitbitParser
from salus.services.parsers.google_fit import GoogleFitParser
from salus.services.parsers.oura import OuraParser


class TestAppleHealthParser:
    def test_can_handle_positive(self):
        parser = AppleHealthExportParser()
        payload = {"HealthData": {"Record": []}}
        assert parser.can_handle(payload) is True

    def test_can_handle_negative(self):
        parser = AppleHealthExportParser()
        assert parser.can_handle({"other": "data"}) is False

    def test_parse(self):
        parser = AppleHealthExportParser()
        payload = {
            "HealthData": {
                "Record": [
                    {"type": "HKQuantityTypeIdentifierStepCount", "startDate": "2026-01-01T08:00:00", "endDate": "2026-01-01T09:00:00", "value": "5000"}
                ]
            }
        }
        records = parser.parse(payload)
        assert len(records) == 1
        assert "StepCount" in records[0].data_type


class TestGoogleFitParser:
    def test_can_handle_positive(self):
        parser = GoogleFitParser()
        assert parser.can_handle({"bucket": []}) is True

    def test_can_handle_negative(self):
        parser = GoogleFitParser()
        assert parser.can_handle({"other": "data"}) is False

    def test_parse(self):
        parser = GoogleFitParser()
        payload = {
            "bucket": [
                {
                    "startTimeMillis": "1700000000000",
                    "endTimeMillis": "1700003600000",
                    "dataset": [
                        {
                            "dataSourceId": "steps",
                            "point": [{"startTimeNanos": "1700000000000000000", "endTimeNanos": "1700000000000000000", "value": [{"intVal": 5000}]}]
                        }
                    ]
                }
            ]
        }
        records = parser.parse(payload)
        assert len(records) == 1
        assert records[0].data_type == "steps"


class TestFitbitParser:
    def test_can_handle_positive(self):
        parser = FitbitParser()
        assert parser.can_handle({"activities-heart": []}) is True

    def test_can_handle_negative(self):
        parser = FitbitParser()
        assert parser.can_handle({"other": "data"}) is False

    def test_parse(self):
        parser = FitbitParser()
        payload = {
            "activities-heart": [
                {"dateTime": "2026-01-01", "value": {"heartRateZones": [], "restingHeartRate": 62}}
            ]
        }
        records = parser.parse(payload)
        assert len(records) == 1
        assert records[0].data_type == "heart_rate"


class TestOuraParser:
    def test_can_handle_positive(self):
        parser = OuraParser()
        assert parser.can_handle({"sleep": [], "readiness": []}) is True

    def test_can_handle_negative(self):
        parser = OuraParser()
        assert parser.can_handle({"sleep": []}) is False

    def test_parse(self):
        parser = OuraParser()
        payload = {
            "sleep": [
                {"id": "s1", "day": "2026-01-01", "bedtime_start": "2026-01-01T22:00:00", "bedtime_end": "2026-01-02T06:00:00", "total_sleep_duration": 25200}
            ],
            "readiness": [
                {"id": "r1", "day": "2026-01-01", "score": 85}
            ]
        }
        records = parser.parse(payload)
        assert len(records) == 2


class TestFlexiblePayloadParserWithNewParsers:
    def test_detects_apple_health(self):
        fpp = FlexiblePayloadParser(parsers=[
            AppleHealthExportParser(),
            GoogleFitParser(),
            FitbitParser(),
            OuraParser(),
            HealthConnectWebhookParser(),
            FlatArrayParser(),
        ])
        payload = {
            "HealthData": {
                "Record": [
                    {"type": "StepCount", "startDate": "2026-01-01T08:00:00", "endDate": "", "value": "5000"}
                ]
            }
        }
        records = fpp.parse(payload)
        assert len(records) == 1

    def test_detects_fitbit(self):
        fpp = FlexiblePayloadParser(parsers=[
            AppleHealthExportParser(),
            FitbitParser(),
            GoogleFitParser(),
            OuraParser(),
        ])
        payload = {
            "activities-heart": [
                {"dateTime": "2026-01-01", "value": {"restingHeartRate": 62}}
            ]
        }
        records = fpp.parse(payload)
        assert len(records) == 1
