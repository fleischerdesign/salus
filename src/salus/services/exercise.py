from salus.models.workout import Exercise
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.exercise_reference import COMMON_EXERCISES


class ExerciseService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def seed_common_exercises(self) -> int:
        session = self.uow.session
        count = 0
        for data in COMMON_EXERCISES:
            if session.get(Exercise, data["id"]) is None:
                session.add(
                    Exercise(
                        id=data["id"],
                        name=data["name"],
                        equipment=data.get("equipment", "barbell"),
                        primary_muscles=data["primary_muscles"],
                        secondary_muscles=data.get("secondary_muscles"),
                        description=data.get("description"),
                        instructions=data.get("instructions"),
                        suggested_rest_seconds=data.get("suggested_rest_seconds", 120),
                        user_id=None,
                    )
                )
                count += 1
        return count

    def get_catalog(self, user_id: str) -> list[Exercise]:
        return self.uow.exercises.find_all_catalog(user_id)
