"""Reference data seeding and synchronization engine."""

import hashlib
import json
import logging
import time
from typing import Any

from sqlmodel import Session

from salus.models.system_config import SystemConfig
from salus.reference_data.registry import REFERENCE_SPECS
from salus.reference_data.types import ReferenceSpec, SeedingItemReport, SeedingReport

logger = logging.getLogger("salus.reference_data")


def _compute_spec_hash(items: list[dict[str, Any]]) -> str:
    """Computes a deterministic SHA-256 hash of the reference items."""
    encoded = json.dumps(items, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class ReferenceDataEngine:
    """Idempotent engine for seeding and synchronizing reference datasets."""

    def __init__(self, specs: tuple[ReferenceSpec, ...] = REFERENCE_SPECS) -> None:
        self.specs = specs

    def seed_all(self, session: Session) -> SeedingReport:
        """Seeds all registered reference datasets into the database."""
        start = time.perf_counter()
        report = SeedingReport()

        for spec in self.specs:
            item_report = self.seed_spec(session, spec)
            report.items.append(item_report)

        session.commit()
        report.duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"Reference data seeded in {report.duration_ms:.2f}ms: "
            f"{report.total_created} created, {report.total_updated} updated"
        )
        return report

    def seed_spec(self, session: Session, spec: ReferenceSpec) -> SeedingItemReport:
        """Seeds a single reference dataset with fast-skip and field diffing."""
        report = SeedingItemReport(name=spec.name, total=len(spec.items))
        spec_hash = _compute_spec_hash(spec.items)
        config_key = f"ref_hash_{spec.name}"

        # Fast SHA-256 skip check
        try:
            stored_config = session.get(SystemConfig, config_key)
            if stored_config and stored_config.value == spec_hash:
                report.skipped_by_hash = True
                report.unchanged = len(spec.items)
                return report
        except Exception:
            stored_config = None

        for item_data in spec.items:
            key_val = item_data[spec.unique_key]
            existing = session.get(spec.model, key_val)

            if existing is None:
                if spec.instantiator is not None:
                    instance = spec.instantiator(item_data)
                else:
                    instance = spec.model(**item_data)
                session.add(instance)
                report.created += 1
            else:
                changed = False
                for field in spec.update_fields:
                    if field in item_data:
                        new_val = item_data[field]
                        old_val = getattr(existing, field, None)
                        if old_val != new_val:
                            setattr(existing, field, new_val)
                            changed = True
                if changed:
                    session.add(existing)
                    report.updated += 1
                else:
                    report.unchanged += 1

        # Store updated hash
        try:
            if stored_config is not None:
                stored_config.value = spec_hash
                session.add(stored_config)
            else:
                session.add(
                    SystemConfig(
                        key=config_key,
                        value=spec_hash,
                        description=f"SHA-256 hash of {spec.name} reference data",
                        category="system",
                        is_secret=False,
                    )
                )
        except Exception:
            pass

        return report
