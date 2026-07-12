from sqlalchemy import asc
from sqlmodel import select

from salus.models.dashboard import DashboardWidget
from salus.repositories.base import Repository


class DashboardWidgetRepository(Repository[DashboardWidget]):
    model = DashboardWidget

    def find_by_user(self, user_id: int) -> list[DashboardWidget]:
        stmt = (
            select(DashboardWidget)
            .where(DashboardWidget.user_id == user_id)
            .order_by(asc(DashboardWidget.position))  # type: ignore[arg-type]
        )
        return list(self.session.exec(stmt).all())

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        for pos, widget_id in enumerate(ordered_ids):
            widget = self.get_by_id(widget_id)
            if widget is not None and widget.user_id == user_id:
                widget.position = pos
                self.update(widget, auto_commit=False)
        self.session.commit()

    def find_by_user_and_metric(
        self, user_id: int, metric_type_id: int
    ) -> DashboardWidget | None:
        stmt = select(DashboardWidget).where(
            DashboardWidget.user_id == user_id,
            DashboardWidget.metric_type_id == metric_type_id,
        )
        return self.session.exec(stmt).first()
