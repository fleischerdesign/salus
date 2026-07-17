from datetime import date, datetime

from sqlmodel import select

from salus.models.medication import (
    Medication,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.repositories.base import Repository


class MedicationRepository(Repository[Medication]):
    model = Medication

    def find_by_user(self, user_id: str) -> list[Medication]:
        return list(
            self.session.exec(
                select(Medication).where(
                    Medication.user_id == user_id,
                    Medication.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Medication.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_active(self, user_id: str) -> list[Medication]:
        return list(
            self.session.exec(
                select(Medication).where(
                    Medication.user_id == user_id,
                    Medication.is_active == True,  # noqa: E712
                    Medication.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Medication.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class MedicationScheduleRepository(Repository[MedicationSchedule]):
    model = MedicationSchedule

    def find_by_medication(self, medication_id: str) -> list[MedicationSchedule]:
        return list(
            self.session.exec(
                select(MedicationSchedule).where(
                    MedicationSchedule.medication_id == medication_id,
                    MedicationSchedule.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )

    def find_by_user(self, user_id: str) -> list[MedicationSchedule]:
        return list(
            self.session.exec(
                select(MedicationSchedule).where(
                    MedicationSchedule.user_id == user_id,
                    MedicationSchedule.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )


class MedicationLogRepository(Repository[MedicationLog]):
    model = MedicationLog

    def find_by_medication(self, medication_id: str) -> list[MedicationLog]:
        return list(
            self.session.exec(
                select(MedicationLog).where(
                    MedicationLog.medication_id == medication_id,
                    MedicationLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(MedicationLog.taken_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_date(self, user_id: str, log_date: date) -> list[MedicationLog]:
        start = datetime(log_date.year, log_date.month, log_date.day, 0, 0, 0)
        end = datetime(log_date.year, log_date.month, log_date.day, 23, 59, 59)
        return list(
            self.session.exec(
                select(MedicationLog).where(
                    MedicationLog.user_id == user_id,
                    MedicationLog.taken_at >= start,
                    MedicationLog.taken_at <= end,
                    MedicationLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )

    def find_by_schedule_and_time(
        self, schedule_id: str, taken_at_start: datetime, taken_at_end: datetime
    ) -> MedicationLog | None:
        stmt = select(MedicationLog).where(
            MedicationLog.schedule_id == schedule_id,
            MedicationLog.taken_at >= taken_at_start,
            MedicationLog.taken_at <= taken_at_end,
            MedicationLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()

    def find_all_by_user(self, user_id: str) -> list[MedicationLog]:
        return list(
            self.session.exec(
                select(MedicationLog).where(
                    MedicationLog.user_id == user_id,
                    MedicationLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(MedicationLog.taken_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class MedicationInventoryRepository(Repository[MedicationInventory]):
    model = MedicationInventory

    def find_by_medication(self, medication_id: str) -> MedicationInventory | None:
        stmt = select(MedicationInventory).where(
            MedicationInventory.medication_id == medication_id,
            MedicationInventory.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()
