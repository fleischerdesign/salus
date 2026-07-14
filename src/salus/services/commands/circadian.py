from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("save_circadian_profile")
class SaveCircadianProfileHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        profile = uow.circadian_profiles.find_by_user(user.id)  # pyright: ignore[reportArgumentType]
        if not profile:
            from salus.models.circadian import CircadianProfile
            profile = CircadianProfile(
                id=payload.get("id"),
                user_id=user.id,  # pyright: ignore[reportArgumentType]
            )
            uow.circadian_profiles.add(profile)
        profile.latitude = payload["latitude"]  # pyright: ignore[reportAttributeAccessIssue]
        profile.longitude = payload["longitude"]  # pyright: ignore[reportAttributeAccessIssue]
        profile.timezone_offset_hours = payload["timezone_offset_hours"]  # pyright: ignore[reportAttributeAccessIssue]
        profile.configured_chronotype = payload.get("configured_chronotype", "intermediate")  # pyright: ignore[reportAttributeAccessIssue]
        uow.session.add(profile)
        uow.commit()
        uow.session.refresh(profile)
        record: dict[str, Any] = {
            "id": profile.id,
            "user_id": profile.user_id,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "timezone_offset_hours": profile.timezone_offset_hours,
            "configured_chronotype": profile.configured_chronotype,
        }
        return CommandResult(status="updated", record=record, id=profile.id)  # pyright: ignore[reportAttributeAccessIssue]