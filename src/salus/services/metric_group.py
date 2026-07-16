from salus.exceptions import NotFoundError
from salus.models.metric_definition import MetricGroup
from salus.repositories.unit_of_work import IUnitOfWork


class MetricGroupService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get_groups_with_preferences(self, user_id: str) -> list[dict]:
        groups = self.uow.metric_groups.find_all()
        result: list[dict] = []

        for group in groups:
            definitions = self.uow.metric_definitions.find_by_group(group.key)
            metrics: list[dict] = []
            for d in definitions:
                pref = self.uow.metric_preferences.find_by_user_and_code(user_id, d.code)
                metrics.append({
                    "code": d.code,
                    "name": d.name,
                    "unit": d.unit,
                    "data_type": d.data_type.value if hasattr(d.data_type, "value") else str(d.data_type),
                    "source_data_type": d.source_data_type,
                    "description": d.description,
                    "sort_order": d.sort_order,
                    "color": pref.color if pref else "#4f46e5",
                    "icon": pref.icon if pref else "monitoring",
                    "widget_size": pref.widget_size if pref else "medium",
                    "widget_enabled": pref.widget_enabled if pref else False,
                    "enabled": pref.enabled if pref else True,
                    "position": pref.position if pref else 0,
                })

            result.append({
                "key": group.key,
                "name": group.name,
                "icon": group.icon,
                "description": group.description,
                "input_mode": group.input_mode,
                "metrics": metrics,
            })

        return result

    def get_by_key(self, key: str) -> MetricGroup:
        group = self.uow.metric_groups.find_by_key(key)
        if group is None:
            raise NotFoundError(f"Metric group '{key}' not found")
        return group
