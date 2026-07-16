import io
import zipfile
import json
import csv
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool
from salus.models.user import User
from salus.models.measurement import Measurement
from salus.models.metric_definition import MetricDefinition
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services._helpers import uid
from salus.services.portability import DataPortabilityService
from datetime import datetime


def test_data_portability_export_import():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        uow = SqlUnitOfWork(session)
        with uow:
            user = User(username="alice", password_hash="hash", email="alice@salus.local")
            uow.users.add(user)
            uow.commit()
            user_id = uid(user)

            mt = MetricDefinition(code="portability_weight", name="Weight", unit="kg", source_data_type="weight")
            uow.metric_definitions.add(mt)
            uow.commit()
            metric_code = mt.code

            m = Measurement(
                user_id=user_id,
                source="test_source",
                metric_code=metric_code,
                value_numeric=75.5,
                start_time=datetime.now(),
            )
            uow.measurements.add(m)
            uow.commit()

    svc = DataPortabilityService(uow)

    zip_bytes_io = svc.export_user_data(user_id)
    zip_bytes = zip_bytes_io.getvalue()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
        namelist = zip_file.namelist()
        assert "profile.json" in namelist
        assert "measurements.csv" in namelist
        assert "workout_plans.json" in namelist
        assert "workout_history.csv" in namelist
        assert "goals.json" in namelist

        profile = json.loads(zip_file.read("profile.json").decode("utf-8"))
        assert profile["username"] == "alice"

        csv_data = zip_file.read("measurements.csv").decode("utf-8")
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        assert len(rows) > 0
        assert rows[0]["source"] == "test_source"
        assert float(rows[0]["value_numeric"]) == 75.5

    import_result = svc.import_user_data(user_id, zip_bytes)
    assert "measurements_imported" in import_result

    new_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(new_zip_buffer, "w", zipfile.ZIP_DEFLATED) as new_zip:
        new_zip.writestr("profile.json", json.dumps({"theme": "dark"}))

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow([
            "source", "data_type", "metric_code", "value_numeric",
            "value_text", "value_json", "start_time", "end_time", "notes", "external_id",
        ])
        csv_writer.writerow([
            "imported_source", "weight", metric_code, "80.0",
            "", "", datetime.now().isoformat(), "", "Imported note", "",
        ])
        new_zip.writestr("measurements.csv", csv_buffer.getvalue())

    new_zip_bytes = new_zip_buffer.getvalue()
    import_result_2 = svc.import_user_data(user_id, new_zip_bytes)
    assert import_result_2["measurements_imported"] == 1

    with Session(engine) as session:
        imported_measurement = session.exec(
            select(Measurement).where(Measurement.source == "imported_source")
        ).first()
        assert imported_measurement is not None
        assert imported_measurement.value_numeric == 80.0
        assert imported_measurement.notes == "Imported note"
