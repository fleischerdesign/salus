import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from salus.exceptions import NotFoundError, ConflictError
from salus.models.sharing import SharingRelationship
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid

logger = logging.getLogger("salus.services.sharing")


class SharingService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def create_relationship(
        self,
        owner_id: int,
        grantee_handle: str,
        metric_type_id: int,
        aggregation_level: str = "daily_summary",
        expiration_days: Optional[int] = None,
    ) -> SharingRelationship:
        """Creates a sharing relationship from a local user to a grantee handle."""
        # 1. Clean handle
        grantee_handle = grantee_handle.strip()
        if not grantee_handle.startswith("@"):
            grantee_handle = f"@{grantee_handle}"

        # 2. Check if metric type exists and belongs to owner
        with self.uow:
            metric = self.uow.metric_types.get_by_id(metric_type_id)
            if not metric or metric.user_id != owner_id:
                raise NotFoundError("Metric type not found or access denied")

            # If it's a local handle (no ':'), check if the user exists
            if ":" not in grantee_handle:
                username = grantee_handle[1:]
                local_user = self.uow.users.get_by_username(username)
                if not local_user:
                    raise NotFoundError(f"Local user '{username}' not found")

            # Check for existing active relationship
            existing = self.uow.sharing_relationships.get_active_relationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=metric_type_id,
            )
            if existing:
                raise ConflictError("Active sharing relationship already exists for this metric and user")

            # Create relationship
            expiration_date = None
            if expiration_days is not None:
                expiration_date = datetime.now(timezone.utc) + timedelta(days=expiration_days)

            # Generate random api_token_hash for remote verification
            import secrets
            token = secrets.token_hex(20)

            rel = SharingRelationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=metric_type_id,
                aggregation_level=aggregation_level,
                expiration_date=expiration_date,
                api_token_hash=token,  # In production, hash it, but here keep it for easy P2P token transfer
            )
            self.uow.sharing_relationships.create(rel)
            self.uow.commit()
            return rel

    def list_relationships(self, owner_id: int) -> list[SharingRelationship]:
        with self.uow:
            return self.uow.sharing_relationships.find_by_owner(owner_id)

    def deactivate_relationship(self, owner_id: int, relationship_id: int) -> None:
        with self.uow:
            rel = self.uow.sharing_relationships.get_by_id(relationship_id)
            if not rel or rel.owner_id != owner_id:
                raise NotFoundError("Sharing relationship not found")
            rel.is_active = False
            self.uow.sharing_relationships.update(rel)
            self.uow.commit()

    def resolve_and_fetch(
        self,
        requester_id: int,
        owner_handle: str,
        data_type: str,
        date_str: str,
    ) -> list[dict]:
        """Resolves handle and queries data (local database read or remote HTTP fetch)."""
        owner_handle = owner_handle.strip()
        if not owner_handle.startswith("@"):
            owner_handle = f"@{owner_handle}"

        # Get requester handle
        with self.uow:
            req_user = self.uow.users.get_by_id(requester_id)
            if not req_user:
                raise NotFoundError("Requester not found")
            requester_handle = f"@{req_user.username}"

        # 1. Local Resolution
        if ":" not in owner_handle:
            owner_username = owner_handle[1:]
            with self.uow:
                owner_user = self.uow.users.get_by_username(owner_username)
                if not owner_user:
                    raise NotFoundError(f"User {owner_username} not found")
                
                # Check for metric type
                metric_types = self.uow.metric_types.find_all(owner_user.id)
                metric = next((m for m in metric_types if m.source_data_type == data_type), None)
                if not metric:
                    return []
                if metric.id is None:
                    raise ValueError("Metric has no persisted id")
                metric_id = metric.id

                # Verify sharing permissions
                rel = self.uow.sharing_relationships.get_active_relationship(
                    owner_id=uid(owner_user),
                    grantee_handle=requester_handle,
                    metric_type_id=metric_id,
                )
                if not rel:
                    # Access Denied
                    raise PermissionError(f"Access denied: no active sharing relationship from {owner_handle}")

                # Query measurements
                raw_measurements = self.uow.measurements.find_all(
                    user_id=uid(owner_user),
                    data_types=[data_type]
                )
                
                # Filter by date
                try:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    target_date = datetime.now(timezone.utc).date()

                day_measurements = [
                    m for m in raw_measurements 
                    if m.start_time.date() == target_date
                ]

                # Enforce aggregation policy
                if rel.aggregation_level == "daily_summary":
                    if not day_measurements:
                        return []
                    # Aggregate value_numeric
                    values = [m.value_numeric for m in day_measurements if m.value_numeric is not None]
                    val = sum(values) if data_type in ("steps", "water") else (sum(values)/len(values) if values else None)
                    return [{
                        "data_type": data_type,
                        "value_numeric": val,
                        "start_time": date_str,
                        "source": "summary",
                        "external_id": f"summary-{owner_username}-{data_type}-{date_str}"
                    }]
                else:
                    # Return raw
                    return [
                        {
                            "data_type": m.data_type,
                            "value_numeric": m.value_numeric,
                            "value_json": m.value_json,
                            "start_time": m.start_time.isoformat(),
                            "source": m.source,
                            "external_id": m.external_id
                        }
                        for m in day_measurements
                    ]

        # 2. Remote Resolution
        else:
            # Under a full remote federation setup, we would fetch the remote endpoint:
            # return self._fetch_remote(...)
            # For Phase 1, we return an empty list or stub to be implemented.
            logger.info(f"Remote federation query to {owner_handle} requested (stubbed)")
            return []
