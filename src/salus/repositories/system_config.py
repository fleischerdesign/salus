from sqlmodel import select

from salus.models.system_config import SystemConfig
from salus.repositories.base import Repository


class SystemConfigRepository(Repository[SystemConfig]):
    model = SystemConfig

    def get_all(self) -> list[SystemConfig]:
        return list(self.session.exec(select(SystemConfig)).all())

    def get_by_key(self, key: str) -> SystemConfig | None:
        return self.session.get(SystemConfig, key)

    def upsert(self, key: str, value: str, **kwargs) -> SystemConfig:
        existing = self.session.get(SystemConfig, key)
        if existing is not None:
            existing.value = value
            for k, v in kwargs.items():
                setattr(existing, k, v)
            return self.update(existing)

        config = SystemConfig(key=key, value=value, **kwargs)
        self.session.add(config)
        self.session.commit()
        self.session.refresh(config)
        return config

    def seed_missing(self, defaults: list[SystemConfig]) -> int:
        created = 0
        for item in defaults:
            if self.session.get(SystemConfig, item.key) is None:
                self.session.add(item)
                created += 1
        if created > 0:
            self.session.commit()
        return created
