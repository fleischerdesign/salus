from sqlmodel import select

from salus.models.workout import Program, ProgramWorkout
from salus.repositories.base import Repository
from salus.repositories.protocols import IProgramRepository, IProgramWorkoutRepository


class ProgramRepository(Repository[Program], IProgramRepository):
    model = Program

    def find_by_user(self, user_id: str) -> list[Program]:
        return list(
            self.session.exec(
                select(Program)
                .where(Program.user_id == user_id)
                .order_by(Program.position, Program.created_at)  # pyright: ignore[reportArgumentType]
            ).all()
        )

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None:
        for pos, program_id in enumerate(ordered_ids):
            program = self.get_by_id(program_id)
            if program is not None and program.user_id == user_id:
                program.position = pos
                self.session.add(program)
        self.session.commit()


class ProgramWorkoutRepository(Repository[ProgramWorkout], IProgramWorkoutRepository):
    model = ProgramWorkout

    def find_by_program(self, program_id: str) -> list[ProgramWorkout]:
        stmt = select(ProgramWorkout).where(ProgramWorkout.program_id == program_id)
        return list(self.session.exec(stmt).all())

    def replace_workouts_for_program(
        self, program_id: str, slots: list[ProgramWorkout]
    ) -> None:
        old = self.find_by_program(program_id)
        for slot in old:
            self.session.delete(slot)
        self.session.flush()
        for slot in slots:
            self.session.add(slot)
