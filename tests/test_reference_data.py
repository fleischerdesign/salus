from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
import salus.models  # noqa: F401

from salus.models.metric_definition import MetricDefinition
from salus.reference_data.engine import ReferenceDataEngine
from salus.reference_data.registry import REFERENCE_SPECS


def test_reference_data_engine_seeding():
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    session = Session(engine)
    try:
        ref_engine = ReferenceDataEngine(REFERENCE_SPECS)

        # 1. First run: Seeds all items
        report1 = ref_engine.seed_all(session)
        assert report1.total_created > 0
        assert report1.total_updated == 0

        # Verify a metric was created
        steps = session.get(MetricDefinition, "steps")
        assert steps is not None
        assert steps.unit == "steps"

        # 2. Second run: Fast SHA-256 skip
        report2 = ref_engine.seed_all(session)
        assert report2.total_created == 0
        assert report2.total_updated == 0
        assert all(item.skipped_by_hash for item in report2.items)

    finally:
        session.close()
