from datetime import date, datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.medication import (
    Medication,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.medication import (
    MedicationCreate,
    MedicationInventoryUpdate,
    MedicationLogCreate,
    MedicationScheduleCreate,
    MedicationUpdate,
)


def _make_dt(d: date, hour: int, minute: int) -> datetime:
    return datetime(d.year, d.month, d.day, hour, minute, 0)


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

    def create(self, data: MedicationCreate, user_id: str) -> Medication:
        m = Medication(
            user_id=user_id,
            name=data.name,
            active_ingredient=data.active_ingredient,
            strength=data.strength,
            form=data.form,
            instructions=data.instructions,
            color_hex=data.color_hex,
            icon=data.icon,
        )
        return self.uow.medications.create(m)

    def update(self, medication_id: str, user_id: str, data: MedicationUpdate) -> Medication:
        m = self.get(medication_id, user_id)
        if data.name is not None:
            m.name = data.name
        if data.active_ingredient is not None:
            m.active_ingredient = data.active_ingredient
        if data.strength is not None:
            m.strength = data.strength
        if data.form is not None:
            m.form = data.form
        if data.instructions is not None:
            m.instructions = data.instructions
        if data.color_hex is not None:
            m.color_hex = data.color_hex
        if data.icon is not None:
            m.icon = data.icon
        if data.is_active is not None:
            m.is_active = data.is_active
        return self.uow.medications.update(m)

    def delete(self, medication_id: str, user_id: str) -> None:
        m = self.get(medication_id, user_id)
        self.uow.medications.delete(m)

    # ── Schedule ──

    def get_schedules(self, medication_id: str, user_id: str) -> list[MedicationSchedule]:
        self.get(medication_id, user_id)
        return self.uow.medication_schedules.find_by_medication(medication_id)

    def add_schedule(
        self, medication_id: str, user_id: str, data: MedicationScheduleCreate
    ) -> MedicationSchedule:
        self.get(medication_id, user_id)
        s = MedicationSchedule(
            medication_id=medication_id,
            user_id=user_id,
            dosage=data.dosage,
            times=data.times,
            days_of_week=data.days_of_week,
            start_date=date.fromisoformat(data.start_date) if data.start_date else date.today(),
            end_date=date.fromisoformat(data.end_date) if data.end_date else None,
        )
        return self.uow.medication_schedules.create(s)

    def delete_schedule(self, schedule_id: str, user_id: str) -> None:
        s = self.uow.medication_schedules.get_by_id(schedule_id)
        if s is None or s.user_id != user_id:
            raise NotFoundError(f"Schedule {schedule_id} not found")
        self.uow.medication_schedules.delete(s)

    # ── Log / Toggle ──

    def log_intake(
        self, medication_id: str, user_id: str, data: MedicationLogCreate
    ) -> MedicationLog:
        self.get(medication_id, user_id)
        now = datetime.now(timezone.utc)
        log = MedicationLog(
            medication_id=medication_id,
            user_id=user_id,
            schedule_id=data.schedule_id,
            taken_at=datetime.fromisoformat(data.taken_at) if data.taken_at else now,
            dosage_taken=data.dosage_taken,
            skipped=data.skipped,
            notes=data.notes,
        )
        return self.uow.medication_logs.create(log)

    def toggle_check(
        self, medication_id: str, user_id: str, schedule_id: str | None, scheduled_time: str | None
    ) -> dict:
        self.get(medication_id, user_id)
        today = date.today()
        if schedule_id and scheduled_time:
            hour, minute = map(int, scheduled_time.split(":"))
            window_start = _make_dt(today, hour, minute)
            window_end = _make_dt(today, 23, 59)
            existing = self.uow.medication_logs.find_by_schedule_and_time(
                schedule_id, window_start, window_end
            )
            if existing:
                existing.deleted_at = datetime.now(timezone.utc)
                self.uow.medication_logs.update(existing)
                return {
                    "taken": False,
                    "skipped": False,
                    "adherence_rate": self._adherence_rate(medication_id, user_id),
                }

        log = MedicationLog(
            medication_id=medication_id,
            user_id=user_id,
            schedule_id=schedule_id,
            taken_at=datetime.now(timezone.utc),
            skipped=False,
        )
        self.uow.medication_logs.create(log)
        return {
            "taken": True,
            "skipped": False,
            "adherence_rate": self._adherence_rate(medication_id, user_id),
        }

    def skip_dose(
        self, medication_id: str, user_id: str, schedule_id: str, scheduled_time: str
    ) -> MedicationLog:
        self.get(medication_id, user_id)
        hour, minute = map(int, scheduled_time.split(":"))
        today = date.today()
        taken_at = _make_dt(today, hour, minute)
        log = MedicationLog(
            medication_id=medication_id,
            user_id=user_id,
            schedule_id=schedule_id,
            taken_at=taken_at,
            skipped=True,
        )
        return self.uow.medication_logs.create(log)

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
        today = date.today()
        today_logs = self.uow.medication_logs.find_by_user_and_date(user_id, today)
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
                    window_start = _make_dt(today, hour, minute)
                    window_end = _make_dt(today, 23, 59)
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

    def update_inventory(
        self, medication_id: str, user_id: str, data: MedicationInventoryUpdate
    ) -> MedicationInventory:
        self.get(medication_id, user_id)
        existing = self.uow.medication_inventories.find_by_medication(medication_id)
        if existing:
            if data.initial_count is not None:
                existing.initial_count = data.initial_count
            if data.remaining_count is not None:
                existing.remaining_count = data.remaining_count
            if data.refill_at_count is not None:
                existing.refill_at_count = data.refill_at_count
            if data.prescription_refills is not None:
                existing.prescription_refills = data.prescription_refills
            if data.next_refill_date is not None:
                existing.next_refill_date = date.fromisoformat(data.next_refill_date)
            return self.uow.medication_inventories.update(existing)

        if data.initial_count is None or data.remaining_count is None or data.refill_at_count is None:
            raise ValueError(
                "initial_count, remaining_count, refill_at_count are required for new inventory"
            )

        inv = MedicationInventory(
            medication_id=medication_id,
            user_id=user_id,
            initial_count=data.initial_count,
            remaining_count=data.remaining_count,
            refill_at_count=data.refill_at_count,
            prescription_refills=data.prescription_refills,
            next_refill_date=date.fromisoformat(data.next_refill_date) if data.next_refill_date else None,
        )
        return self.uow.medication_inventories.create(inv)
