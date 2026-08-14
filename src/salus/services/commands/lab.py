from __future__ import annotations

from datetime import date, datetime, timezone, tzinfo
from typing import Any, TYPE_CHECKING

from salus.models.lab import LabMarker, LabPanel, LabResult
from salus.models.measurement import Measurement
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.serialization import serialize_record
from salus.services.timezone import start_of_local_day, today_in_tz, user_tz
from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User
    from salus.repositories.unit_of_work import IUnitOfWork

LAB_SOURCE = "lab"

_PANEL_FIELDS = (
    "id", "user_id", "collection_date", "lab_name", "fasting",
    "notes", "attachment_path", "created_at", "updated_at", "deleted_at",
)

_RESULT_FIELDS = (
    "id", "panel_id", "user_id", "metric_code", "value", "unit",
    "is_abnormal", "reference_low", "reference_high", "created_at",
    "updated_at", "deleted_at",
)


def _parse_date(value: str | None, tz: tzinfo) -> date:
    if value:
        return date.fromisoformat(value)
    return today_in_tz(tz)


def _panel_start(collection_date: date, tz: tzinfo) -> datetime:
    return start_of_local_day(collection_date, tz)


def _marker_defaults(uow: IUnitOfWork, metric_code: str) -> LabMarker | None:
    return uow.lab_markers.find_by_code(metric_code)


def _resolve_result(
    uow: IUnitOfWork, user_id: str, panel_id: str, collection_date: date, raw: dict[str, Any]
) -> LabResult:
    metric_code = raw.get("metric_code") or ""
    marker = _marker_defaults(uow, metric_code)

    reference_low = raw.get("reference_low")
    if reference_low is None and marker is not None:
        reference_low = marker.reference_low
    reference_high = raw.get("reference_high")
    if reference_high is None and marker is not None:
        reference_high = marker.reference_high

    value = float(raw["value"])
    is_abnormal = raw.get("is_abnormal")
    if is_abnormal is None:
        is_abnormal = _out_of_range(value, reference_low, reference_high)

    now = datetime.now(timezone.utc)
    return LabResult(
        id=raw.get("id") or uuid7_str(),
        panel_id=panel_id,
        user_id=user_id,
        metric_code=metric_code,
        value=value,
        unit=raw.get("unit"),
        is_abnormal=bool(is_abnormal),
        reference_low=reference_low,
        reference_high=reference_high,
        created_at=now,
        updated_at=now,
    )


def _out_of_range(
    value: float, reference_low: float | None, reference_high: float | None
) -> bool:
    if reference_low is not None and value < reference_low:
        return True
    if reference_high is not None and value > reference_high:
        return True
    return False


def _measurement_for_result(result: LabResult, start_time: datetime) -> Measurement:
    return Measurement(
        user_id=result.user_id,
        metric_code=result.metric_code,
        source_data_type=LAB_SOURCE,
        source=LAB_SOURCE,
        value_numeric=result.value,
        start_time=start_time,
        external_id=result.id,
    )


def _delete_measurement(uow: IUnitOfWork, external_id: str) -> None:
    existing = uow.measurements.find_by_external_id(external_id, LAB_SOURCE)
    if existing:
        uow.measurements.delete(existing)


@register("create_lab_panel")
class CreateLabPanelHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        tz = user_tz(user)
        collection_date = _parse_date(payload.get("collection_date"), tz)
        panel_id = payload.get("id") or uuid7_str()

        now = datetime.now(timezone.utc)
        panel = LabPanel(
            id=panel_id,
            user_id=user_id,
            collection_date=collection_date,
            lab_name=payload.get("lab_name"),
            fasting=bool(payload.get("fasting", False)),
            notes=payload.get("notes"),
            attachment_path=payload.get("attachment_path"),
            created_at=now,
            updated_at=now,
        )
        uow.lab_panels.add(panel)

        start_time = _panel_start(collection_date, tz)
        for raw in payload.get("results", []):
            result = _resolve_result(uow, user_id, panel.id or "", collection_date, raw)
            uow.lab_results.add(result)
            uow.measurements.add(_measurement_for_result(result, start_time))

        uow.commit()
        uow.session.refresh(panel)
        return CommandResult(
            status="created",
            id=panel.id,
            record=serialize_record(panel, list(_PANEL_FIELDS)),
        )


@register("update_lab_panel")
class UpdateLabPanelHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        panel_id = payload.get("id")
        if not panel_id:
            return CommandResult(status="error", message="id is required")

        panel = uow.lab_panels.get_by_id(panel_id)
        if not panel or panel.user_id != user_id:
            return CommandResult(status="not_found", message="Lab panel not found")

        if "collection_date" in payload and payload["collection_date"] is not None:
            panel.collection_date = _parse_date(payload.get("collection_date"), user_tz(user))
        if "lab_name" in payload:
            panel.lab_name = payload.get("lab_name")
        if "fasting" in payload:
            panel.fasting = bool(payload.get("fasting"))
        if "notes" in payload:
            panel.notes = payload.get("notes")
        if "attachment_path" in payload:
            panel.attachment_path = payload.get("attachment_path")
        panel.updated_at = datetime.now(timezone.utc)
        uow.lab_panels.add(panel)

        if "results" in payload:
            for old in uow.lab_results.find_by_panel(panel_id):
                _delete_measurement(uow, old.id or "")
                uow.lab_results.delete(old)

            start_time = _panel_start(panel.collection_date, user_tz(user))
            for raw in payload.get("results", []):
                result = _resolve_result(uow, user_id, panel_id, panel.collection_date, raw)
                uow.lab_results.add(result)
                uow.measurements.add(_measurement_for_result(result, start_time))

        uow.commit()
        uow.session.refresh(panel)
        return CommandResult(
            status="updated",
            id=panel.id,
            record=serialize_record(panel, list(_PANEL_FIELDS)),
        )


@register("delete_lab_panel")
class DeleteLabPanelHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        panel_id = payload.get("id")
        if not panel_id:
            return CommandResult(status="error", message="id is required")

        panel = uow.lab_panels.get_by_id(panel_id)
        if not panel or panel.user_id != user_id:
            return CommandResult(status="deleted", id=panel_id)

        for result in uow.lab_results.find_by_panel(panel_id):
            _delete_measurement(uow, result.id or "")
            uow.lab_results.delete(result)
        uow.lab_panels.delete(panel)
        uow.commit()
        return CommandResult(status="deleted", id=panel_id)
