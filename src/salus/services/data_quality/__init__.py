"""Data-quality domain (ADR-007): write-time checks, sweep service, and jobs.

Public API re-exported for the wiring layer and command handlers. Write-hook
registration is explicit (``register_write_hooks``, called from ``main.create_app``)
rather than an import side-effect.
"""
from salus.services.data_quality.checks import (
    after_measurement_write,
    check_measurement,
    register_write_hooks,
)
from salus.services.data_quality.jobs import DataQualityCleanupJob, DataQualityRecheckJob
from salus.services.data_quality.service import DataQualityService

__all__ = [
    "DataQualityService",
    "DataQualityRecheckJob",
    "DataQualityCleanupJob",
    "check_measurement",
    "after_measurement_write",
    "register_write_hooks",
]
