from salus.exceptions import ConflictError, NotFoundError
from salus.models.metric_definition import MetricDefinition
from salus.models.metric_preference import UserMetricPreference
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas import MetricPreferenceCreate


class MetricDefinitionService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get(self, metric_code: str, user_id: str) -> MetricDefinition | UserMetricPreference:
        definition = self.uow.metric_definitions.find_by_code(metric_code)
        preference = self.uow.metric_preferences.find_by_user_and_code(user_id, metric_code)
        if definition is None and preference is None:
            raise NotFoundError(f"Metric '{metric_code}' not found")
        return preference if preference is not None else definition  # type: ignore[return-value]

    def find_all(self, user_id: str) -> list[MetricDefinition | UserMetricPreference]:
        definitions = self.uow.metric_definitions.find_all()
        preferences = self.uow.metric_preferences.find_all(user_id)
        return list(definitions) + list(preferences)

    def create(self, data: MetricPreferenceCreate, user_id: str) -> UserMetricPreference:
        existing = self.uow.metric_preferences.find_by_user_and_code(user_id, data.name)
        if existing is not None:
            raise ConflictError(f"Metric preference '{data.name}' already exists")
        definition = self.uow.metric_definitions.find_by_code(data.name)
        if definition is None:
            raise NotFoundError(f"Metric definition '{data.name}' not found")
        preference = UserMetricPreference(
            user_id=user_id,
            metric_code=data.name,
            color=data.color,
            icon=data.icon,
            enabled=True,
        )
        return self.uow.metric_preferences.create(preference)

    def update(
        self, metric_code: str, user_id: str, data: MetricPreferenceCreate
    ) -> UserMetricPreference:
        preference = self.uow.metric_preferences.find_by_user_and_code(user_id, metric_code)
        if preference is None:
            raise NotFoundError(f"Metric preference '{metric_code}' not found")
        if data.name != metric_code:
            existing = self.uow.metric_preferences.find_by_user_and_code(user_id, data.name)
            if existing is not None:
                raise ConflictError(f"Metric preference '{data.name}' already exists")
            preference.metric_code = data.name
        preference.color = data.color
        preference.icon = data.icon
        return self.uow.metric_preferences.update(preference)

    def delete(self, metric_code: str, user_id: str) -> None:
        preference = self.uow.metric_preferences.find_by_user_and_code(user_id, metric_code)
        if preference is None:
            raise NotFoundError(f"Metric preference '{metric_code}' not found")
        self.uow.metric_preferences.delete(preference)
