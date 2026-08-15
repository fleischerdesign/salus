from datetime import date, datetime, time, timezone, tzinfo

from salus.exceptions import NotFoundError
from salus.models.medication import (
    Medication,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.timezone import local_day_range, today_in_tz, tz_for


END_OF_DAY_HOUR = 23
END_OF_DAY_MINUTE = 59


def _make_dt(d: date, hour: int, minute: int, tz: tzinfo) -> datetime:
    """Naive-UTC instant of the given local wall-clock time in ``tz``."""
    return datetime.combine(d, time(hour, minute), tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None)


class MedicationService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    # ── Medication CRUD ──

    def find_all(self, user_id: str) -> list[Medication]:
        return self.uow.medications.find_by_user(user_id)

    def get(self, medication_id: str, user_id: str) -> Medication:
        m = self.uow.medications.get_by_id(medication_id)
        if m is None or m.user_id != user_id:
            raise NotFoundError(f"Medication {medication_id} not found")
        return m

    # ── Schedule ──

    def get_schedules(self, medication_id: str, user_id: str) -> list[MedicationSchedule]:
        self.get(medication_id, user_id)
        return self.uow.medication_schedules.find_by_medication(medication_id)

    # ── Log ──

    def get_logs(self, medication_id: str, user_id: str) -> list[MedicationLog]:
        self.get(medication_id, user_id)
        return self.uow.medication_logs.find_by_medication(medication_id)

    def _adherence_rate(self, medication_id: str, user_id: str) -> float:
        logs = self.uow.medication_logs.find_by_medication(medication_id)
        if not logs:
            return 0.0
        taken = sum(1 for log in logs if not log.skipped)
        return round(taken / len(logs), 3)

    # ── Today ──

    def get_today(self, user_id: str) -> dict:
        medications = self.uow.medications.find_active(user_id)
        tz = tz_for(self.uow.session, user_id)
        today = today_in_tz(tz)
        start, end = local_day_range(today, tz)
        today_logs = self.uow.medication_logs.find_by_user_and_range(user_id, start, end)
        schedules = self.uow.medication_schedules.find_by_user(user_id)

        sched_map: dict[str, list[MedicationSchedule]] = {}
        for s in schedules:
            sched_map.setdefault(s.medication_id, []).append(s)

        items = []
        for med in medications:
            med_schedules = sched_map.get(med.id or "", [])
            for sched in med_schedules:
                if sched.days_of_week and today.isoweekday() not in sched.days_of_week:
                    continue
                if sched.start_date and today < sched.start_date:
                    continue
                if sched.end_date and today > sched.end_date:
                    continue
                for t in sched.times:
                    hour, minute = map(int, t.split(":"))
                    window_start = _make_dt(today, hour, minute, tz)
                    window_end = _make_dt(today, END_OF_DAY_HOUR, END_OF_DAY_MINUTE, tz)
                    existing = next(
                        (
                            log
                            for log in today_logs
                            if log.medication_id == med.id
                            and log.schedule_id == sched.id
                            and log.taken_at
                            and log.taken_at >= window_start
                            and log.taken_at <= window_end
                        ),
                        None,
                    )
                    items.append({
                        "medication_id": med.id or "",
                        "medication_name": med.name,
                        "color_hex": med.color_hex,
                        "icon": med.icon,
                        "schedule_id": sched.id,
                        "dosage": sched.dosage,
                        "time": t,
                        "taken": existing is not None and not existing.skipped,
                        "skipped": existing is not None and existing.skipped,
                        "taken_at": existing.taken_at.isoformat() if existing and existing.taken_at else None,
                        "log_id": existing.id if existing else None,
                    })

        as_needed = [m for m in medications if not sched_map.get(m.id or "")]
        return {"items": items, "as_needed": as_needed}

    # ── Inventory ──

    def get_inventory(self, medication_id: str, user_id: str) -> MedicationInventory | None:
        self.get(medication_id, user_id)
        return self.uow.medication_inventories.find_by_medication(medication_id)
