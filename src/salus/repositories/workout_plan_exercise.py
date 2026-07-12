from sqlmodel import select

from salus.models.workout import WorkoutPlanExercise
from salus.repositories.base import Repository
from salus.repositories.protocols import IWorkoutPlanExerciseRepository


class WorkoutPlanExerciseRepository(Repository[WorkoutPlanExercise], IWorkoutPlanExerciseRepository):
    model = WorkoutPlanExercise

    def find_by_plan(self, plan_id: int) -> list[WorkoutPlanExercise]:
        stmt = select(WorkoutPlanExercise).where(
            WorkoutPlanExercise.plan_id == plan_id
        )
        return list(self.session.exec(stmt).all())

    def replace_exercises_for_plan(
        self, plan_id: int, exercises: list[WorkoutPlanExercise]
    ) -> None:
        old = self.find_by_plan(plan_id)
        for ex in old:
            self.session.delete(ex)
        self.session.flush()
        for ex in exercises:
            self.session.add(ex)
