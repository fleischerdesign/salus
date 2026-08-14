from sqlmodel import col, select

from salus.models.data_quality import DataQualityFlag
from salus.repositories.base import Repository


class DataQualityFlagRepository(Repository[DataQualityFlag]):
    model = DataQualityFlag

    def find_by_user(self, user_id: str, limit: int = 100) -> list[DataQualityFlag]:
        return list(
            self.session.exec(
                select(DataQualityFlag).where(
                    DataQualityFlag.user_id == user_id,
                ).order_by(col(DataQualityFlag.created_at).desc()).limit(limit)
            ).all()
        )

    def find_by_measurement(self, measurement_id: str) -> list[DataQualityFlag]:
        return list(
            self.session.exec(
                select(DataQualityFlag).where(
                    DataQualityFlag.measurement_id == measurement_id,
                ).order_by(col(DataQualityFlag.created_at).desc())
            ).all()
        )
