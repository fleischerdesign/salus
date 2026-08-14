from datetime import date

from sqlmodel import select

from salus.models.lab import LabMarker, LabPanel, LabResult
from salus.repositories.base import Repository


class LabMarkerRepository(Repository[LabMarker]):
    model = LabMarker

    def find_all(self) -> list[LabMarker]:
        return list(self.session.exec(select(LabMarker)).all())

    def find_by_code(self, code: str) -> LabMarker | None:
        return self.session.get(LabMarker, code)


class LabPanelRepository(Repository[LabPanel]):
    model = LabPanel

    def find_by_user(self, user_id: str) -> list[LabPanel]:
        return list(
            self.session.exec(
                select(LabPanel).where(
                    LabPanel.user_id == user_id,
                    LabPanel.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(LabPanel.collection_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_date_range(
        self, user_id: str, since: date, until: date
    ) -> list[LabPanel]:
        return list(
            self.session.exec(
                select(LabPanel).where(
                    LabPanel.user_id == user_id,
                    LabPanel.collection_date >= since,
                    LabPanel.collection_date <= until,
                    LabPanel.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(LabPanel.collection_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class LabResultRepository(Repository[LabResult]):
    model = LabResult

    def find_by_panel(self, panel_id: str) -> list[LabResult]:
        return list(
            self.session.exec(
                select(LabResult).where(
                    LabResult.panel_id == panel_id,
                    LabResult.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )
