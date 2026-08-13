"""Community activity feed aggregation for the sync payload."""
from sqlalchemy.orm import selectinload

from salus.models.sharing import SharingRelationship
from salus.models.workout import WorkoutSession
from sqlmodel import select


def community_activity_feed(s, user_id: str, username: str) -> list[dict]:
    user_handle = f"@{username}"
    activities: list[dict] = []

    incoming = s.exec(
        select(SharingRelationship)
        .options(selectinload(SharingRelationship.owner))  # type: ignore[arg-type]
        .where(
            SharingRelationship.grantee_handle == user_handle,
            SharingRelationship.status == "active",
        )
    ).all()

    for rel in incoming:
        owner = rel.owner
        activities.append({
            "id": rel.id,
            "friend_name": owner.username if owner else f"user_{rel.owner_id}",
            "activity_type": "steps",
            "activity_description": "shared health data with you",
            "time": rel.created_at.isoformat() if rel.created_at else None,
        })

    outgoing = s.exec(
        select(SharingRelationship).where(
            SharingRelationship.owner_id == user_id,
            SharingRelationship.status == "active",
        )
    ).all()

    for rel in outgoing:
        activities.append({
            "id": rel.id,
            "friend_name": rel.grantee_handle,
            "activity_type": "steps",
            "activity_description": "started sharing health data",
            "time": rel.created_at.isoformat() if rel.created_at else None,
        })

    sessions = s.exec(
        select(WorkoutSession).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.completed_at.is_not(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        ).order_by(WorkoutSession.completed_at.desc()).limit(20)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    ).all()

    for se in sessions:
        activities.append({
            "id": se.id,
            "friend_name": username,
            "activity_type": "workout",
            "activity_description": "completed a workout",
            "time": se.completed_at.isoformat() if se.completed_at else None,
        })

    activities.sort(key=lambda a: a.get("time") or "", reverse=True)
    return activities[:50]
