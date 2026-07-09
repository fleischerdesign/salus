import io
import zipfile
import json
import csv
import pytest
from sqlmodel import Session, select
from salus.models.user import User
from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models.workout import WorkoutPlan
from salus.services.password import hash_password
from datetime import datetime

def test_data_portability_flow(authenticated_client):
    engine = authenticated_client.app.state.engine
    
    # 1. Add some initial test data (Measurement, Goal, Plan) for Alice
    with Session(engine) as session:
        alice = session.exec(select(User).where(User.username == "alice")).first()
        assert alice is not None
        alice_id = alice.id
        
        # Add a test measurement
        m = Measurement(
            user_id=alice_id,
            source="test_source",
            data_type="weight",
            metric_type_id=1,
            value_numeric=75.5,
            start_time=datetime.now(),
        )
        session.add(m)
        session.commit()

    # 2. Test GET Export Data
    response = authenticated_client.get("/settings/privacy/export")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/zip"
    
    # Read the response bytes and parse the ZIP file
    zip_bytes = response.content
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        namelist = zip_file.namelist()
        assert "profile.json" in namelist
        assert "measurements.csv" in namelist
        assert "workout_plans.json" in namelist
        assert "workout_history.csv" in namelist
        assert "goals.json" in namelist
        
        # Verify profile content
        profile = json.loads(zip_file.read("profile.json").decode("utf-8"))
        assert profile["username"] == "alice"
        
        # Verify measurements CSV content
        csv_data = zip_file.read("measurements.csv").decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        assert len(rows) > 0
        assert rows[0]["source"] == "test_source"
        assert float(rows[0]["value_numeric"]) == 75.5

    # 3. Test POST Import Data (restore the exported ZIP)
    import_response = authenticated_client.post(
        "/settings/privacy/import",
        files={"import_file": ("salus_export.zip", zip_bytes, "application/zip")},
    )
    assert import_response.status_code == 200
    # Since we imported duplicates of the existing records, it should report:
    # "Import finished. No new data was added (all records were duplicates)."
    assert "No new data was added" in import_response.text

    # 4. Now modify the ZIP file to add a new measurement and import it to test insertion
    new_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(new_zip_buffer, "w", zipfile.ZIP_DEFLATED) as new_zip:
        new_zip.writestr("profile.json", json.dumps({"theme": "dark"}))
        
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow([
            "source", "data_type", "metric_type_id", "value_numeric",
            "value_text", "value_json", "start_time", "end_time", "notes", "external_id"
        ])
        csv_writer.writerow([
            "imported_source", "weight", "1", "80.0",
            "", "", datetime.now().isoformat(), "", "Imported note", ""
        ])
        new_zip.writestr("measurements.csv", csv_buffer.getvalue())
        
    new_zip_bytes = new_zip_buffer.getvalue()
    
    import_response_2 = authenticated_client.post(
        "/settings/privacy/import",
        files={"import_file": ("salus_export.zip", new_zip_bytes, "application/zip")},
    )
    assert import_response_2.status_code == 200
    assert "Successfully imported" in import_response_2.text
    assert "1 measurements" in import_response_2.text

    # Verify that the database now contains the newly imported measurement
    with Session(engine) as session:
        imported_measurement = session.exec(
            select(Measurement).where(Measurement.source == "imported_source")
        ).first()
        assert imported_measurement is not None
        assert imported_measurement.value_numeric == 80.0
        assert imported_measurement.notes == "Imported note"
