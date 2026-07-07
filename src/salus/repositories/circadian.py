from sqlmodel import select
from typing import Optional

from salus.models.circadian import CircadianProfile
from salus.repositories.base import Repository


class CircadianProfileRepository(Repository[CircadianProfile]):
    model = CircadianProfile

    def find_by_user(self, user_id: int) -> Optional[CircadianProfile]:
        stmt = (
            select(CircadianProfile).where(CircadianProfile.user_id == user_id).limit(1)
        )
        return self.session.exec(stmt).first()
