from salus.models.lab import LabMarker
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.lab_reference import LAB_MARKERS


class LabService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def seed_markers(self) -> int:
        session = self.uow.session
        count = 0
        for marker in LAB_MARKERS:
            if session.get(LabMarker, marker["code"]) is None:
                session.add(LabMarker(
                    code=marker["code"],
                    category=marker["category"],
                    reference_low=marker.get("reference_low"),
                    reference_high=marker.get("reference_high"),
                    optimal_low=marker.get("optimal_low"),
                    optimal_high=marker.get("optimal_high"),
                    description=marker.get("description"),
                ))
                count += 1
        return count
