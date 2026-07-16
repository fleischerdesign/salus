from sqlmodel import select

from salus.models.metric_preference import UserMetricPreference
from salus.repositories.base import Repository
from salus.repositories.protocols import IMetricPreferenceRepository


class MetricPreferenceRepository(Repository[UserMetricPreference], IMetricPreferenceRepository):
    model = UserMetricPreference

    def find_all(self, user_id: str) -> list[UserMetricPreference]:
        return list(self.session.exec(
            select(UserMetricPreference)
            .where(UserMetricPreference.user_id == user_id)
            .order_by(UserMetricPreference.position)  # pyright: ignore[reportArgumentType]
        ).all())

    def find_by_user_and_code(self, user_id: str, metric_code: str) -> UserMetricPreference | None:
        return self.session.exec(
            select(UserMetricPreference)
            .where(UserMetricPreference.user_id == user_id)
            .where(UserMetricPreference.metric_code == metric_code)
        ).first()

    def reorder(self, user_id: str, ordered_codes: list[str]) -> None:
        for idx, code in enumerate(ordered_codes):
            pref = self.find_by_user_and_code(user_id, code)
            if pref:
                pref.position = idx
                self.session.add(pref)
        self.session.flush()
