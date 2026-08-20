from sqlmodel import select

from salus.models.workout import WorkoutExercise
from salus.repositories.base import Repository
from salus.repositories.protocols import IWorkoutExerciseRepository


class WorkoutExerciseRepository(Repository[WorkoutExercise], IWorkoutExerciseRepository):
    model = WorkoutExercise

    def find_by_workout(self, workout_id: str) -> list[WorkoutExercise]:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.workout_id == workout_id
        )
        return list(self.session.exec(stmt).all())

    def replace_exercises_for_workout(
        self, workout_id: str, exercises: list[WorkoutExercise]
    ) -> None:
        old = self.find_by_workout(workout_id)
        for ex in old:
            self.session.delete(ex)
        self.session.flush()
        for ex in exercises:
            self.session.add(ex)
