import json as _json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, TYPE_CHECKING
from urllib.parse import urlparse

import httpx

from salus.config import settings
from salus.exceptions import ForbiddenError, NotFoundError
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid, parse_date
from salus.services.sharing._http import retry_http_request

if TYPE_CHECKING:
    from salus.services.sharing.keys import FederationKeyService
    from salus.services.sharing.discovery import FederationDiscoveryService
    from salus.services.sharing.relationship import RelationshipService

logger = logging.getLogger("salus.services.sharing.resolver")


class FederationDataResolver:
    def __init__(
        self,
        uow: IUnitOfWork,
        key_svc: "FederationKeyService",
        discovery_svc: "FederationDiscoveryService",
        relationship_svc: "RelationshipService",
    ) -> None:
        self.uow = uow
        self.key_svc = key_svc
        self.discovery_svc = discovery_svc
        self.relationship_svc = relationship_svc

    def resolve_and_fetch(
        self,
        requester_id: str,
        owner_handle: str,
        data_type: str,
        date_str: str,
        force_refresh: bool = False,
    ) -> list[dict]:
        owner_handle = self.relationship_svc.normalize_handle(owner_handle)

        with self.uow:
            req_user = self.uow.users.get_by_id(requester_id)
            if not req_user:
                raise NotFoundError("Requester not found")

        if not self.relationship_svc.is_remote(owner_handle):
            return self._resolve_local(
                owner_handle, f"@{req_user.username}", data_type, date_str
            )
        else:
            if not force_refresh:
                with self.uow:
                    cached = self.uow.federated_measurement_cache.get_cache(
                        owner_handle, data_type, date_str, max_age_seconds=900
                    )
                    if cached:
                        try:
                            return (
                                _json.loads(cached.value_json)
                                if cached.value_json
                                else []
                            )
                        except Exception:
                            logger.debug("Failed to parse cached measurement JSON", exc_info=True)

            data = self._fetch_remote(owner_handle, data_type, date_str)

            with self.uow:
                self.uow.federated_measurement_cache.upsert_cache(
                    owner_handle=owner_handle,
                    data_type=data_type,
                    date_str=date_str,
                    value_numeric=None,
                    value_json=_json.dumps(data),
                )

            return data

    def _resolve_local(
        self, owner_handle: str, requester_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        owner_username = owner_handle[1:]
        with self.uow:
            owner_user = self.uow.users.get_by_username(owner_username)
            if not owner_user:
                raise NotFoundError(f"User {owner_username} not found")

            metric_types = self.uow.metric_types.find_all(owner_user.id)
            metric = next(
                (m for m in metric_types if m.source_data_type == data_type), None
            )
            if not metric:
                return []
            if metric.id is None:
                raise ValueError("Metric has no persisted id")
            metric_id = metric.id

            rel = self.uow.sharing_relationships.get_active_relationship(
                owner_id=uid(owner_user),
                grantee_handle=requester_handle,
                metric_type_id=metric_id,
            )
            if not rel:
                raise ForbiddenError(
                    f"Access denied: no active sharing relationship from {owner_handle}"
                )

            raw_measurements = self.uow.measurements.find_all(
                user_id=uid(owner_user),
                data_types=[data_type],
            )

            target_date = parse_date(date_str) or datetime.now(timezone.utc).date()

            day_measurements = [
                m for m in raw_measurements if m.start_time.date() == target_date
            ]

            if rel.aggregation_level == "daily_summary":
                if not day_measurements:
                    return []
                values = [
                    m.value_numeric
                    for m in day_measurements
                    if m.value_numeric is not None
                ]
                val = (
                    sum(values)
                    if data_type in ("steps", "water")
                    else (sum(values) / len(values) if values else None)
                )
                return [
                    {
                        "data_type": data_type,
                        "value_numeric": val,
                        "start_time": date_str,
                        "source": "summary",
                        "external_id": f"summary-{owner_username}-{data_type}-{date_str}",
                    }
                ]
            else:
                return [
                    {
                        "data_type": m.data_type,
                        "value_numeric": m.value_numeric,
                        "value_json": m.value_json,
                        "start_time": m.start_time.isoformat(),
                        "source": m.source,
                        "external_id": m.external_id,
                    }
                    for m in day_measurements
                ]

    def _fetch_remote(
        self, owner_handle: str, data_type: str, date_str: str
    ) -> list[dict]:
        parts = owner_handle[1:].split(":", 1)
        if len(parts) != 2:
            logger.warning(f"Invalid remote handle format: {owner_handle}")
            return []

        username, _ = parts
        endpoints = self.discovery_svc.resolve_remote_endpoints(owner_handle)
        remote_url = endpoints["sharing"]

        with self.uow:
            active_rel = self.uow.sharing_relationships.find_active_for_remote_owner(
                owner_handle, data_type
            )
            local_user = active_rel.owner if active_rel else None
            local_username = local_user.username if local_user else None

        if not active_rel or not local_username:
            logger.warning(f"No active federation relationship for {owner_handle}")
            return []

        local_domain = urlparse(settings.oauth_redirect_base).netloc
        requester_handle = f"@{local_username}:{local_domain}"

        query_params = {
            "owner_username": username,
            "data_type": data_type,
            "date": date_str,
        }
        req_url = httpx.URL(remote_url, params=query_params)
        sig_headers = self.key_svc.sign_request(requester_handle, "GET", str(req_url))

        token = active_rel.api_token_hash
        if token:
            sig_headers["Authorization"] = f"Bearer {token}"

        def _do_request():
            return httpx.get(
                remote_url,
                params=query_params,
                headers=sig_headers,
                timeout=5.0,
            )

        resp = retry_http_request(
            _do_request,
            operation_name=f"remote federation fetch for {owner_handle}",
        )
        if resp is not None and resp.is_success:
            payload = resp.json()
            return payload.get("data", [])

        return []

    def get_feed_activities(self, user_id: str) -> list[dict]:
        today = datetime.now(timezone.utc).date()
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        activities = []

        with self.uow:
            user = self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")
            user_handle = f"@{user.username}"

            local_incoming = self.uow.sharing_relationships.find_active_by_grantee(
                user_handle
            )

            remote_connections = self.uow.sharing_relationships.find_active_by_owner_id(
                user_id
            )

            friends_dict: dict[str, dict[str, Any]] = {}
            for rel in local_incoming:
                if rel.owner_id not in friends_dict:
                    friends_dict[rel.owner_id] = {
                        "user": rel.owner,
                        "metrics": [],
                    }
                friends_dict[rel.owner_id]["metrics"].append(
                    rel.metric_type.source_data_type
                )

            for friend_id, friend_data in friends_dict.items():
                friend_user = friend_data["user"]
                shared_types = friend_data["metrics"]

                sessions = self.uow.workout_sessions.find_completed_in_range(
                    friend_id,
                    three_days_ago,
                    datetime.max.replace(tzinfo=timezone.utc),
                )

                for sess in sessions:
                    activities.append(
                        {
                            "type": "workout",
                            "friend_name": friend_user.username,
                            "time": sess.completed_at,
                            "title": sess.plan.name if sess.plan else "Workout Session",
                            "notes": sess.notes,
                            "id": f"workout-{sess.id}",
                        }
                    )

                for data_type in shared_types:
                    if data_type not in ("steps", "weight"):
                        continue
                    raw_measurements = self.uow.measurements.find_all(
                        user_id=friend_id,
                        data_types=[data_type],
                    )
                    for offset in range(3):
                        day = today - timedelta(days=offset)
                        day_measurements = [
                            m
                            for m in raw_measurements
                            if m.start_time.date() == day
                            and m.value_numeric is not None
                        ]
                        if day_measurements:
                            if data_type == "steps":
                                val = sum(
                                    m.value_numeric
                                    for m in day_measurements
                                    if m.value_numeric is not None
                                )
                                if val > 0:
                                    activities.append(
                                        {
                                            "type": "steps",
                                            "friend_name": friend_user.username,
                                            "time": datetime.combine(
                                                day,
                                                datetime.min.time(),
                                                tzinfo=timezone.utc,
                                            ),
                                            "value": int(val),
                                            "id": f"steps-{friend_id}-{day.isoformat()}",
                                        }
                                    )
                            elif data_type == "weight":
                                val = day_measurements[-1].value_numeric
                                if val is not None and val > 0:
                                    activities.append(
                                        {
                                            "type": "weight",
                                            "friend_name": friend_user.username,
                                            "time": datetime.combine(
                                                day,
                                                datetime.min.time(),
                                                tzinfo=timezone.utc,
                                            ),
                                            "value": val,
                                            "id": f"weight-{friend_id}-{day.isoformat()}",
                                        }
                                    )

            remote_peers = {}
            for rel in remote_connections:
                if self.relationship_svc.is_remote(rel.grantee_handle):
                    if rel.grantee_handle not in remote_peers:
                        remote_peers[rel.grantee_handle] = []
                    remote_peers[rel.grantee_handle].append(
                        rel.metric_type.source_data_type
                    )

        for remote_handle, shared_types in remote_peers.items():
            for data_type in shared_types:
                if data_type not in ("steps", "weight"):
                    continue
                for offset in range(3):
                    day = today - timedelta(days=offset)
                    day_str = day.strftime("%Y-%m-%d")
                    try:
                        data = self.resolve_and_fetch(
                            requester_id=user_id,
                            owner_handle=remote_handle,
                            data_type=data_type,
                            date_str=day_str,
                        )
                        for item in data:
                            val = item.get("value_numeric")
                            if val is not None and val > 0:
                                activities.append(
                                    {
                                        "type": data_type,
                                        "friend_name": remote_handle,
                                        "time": datetime.combine(
                                            day,
                                            datetime.min.time(),
                                            tzinfo=timezone.utc,
                                        ),
                                        "value": int(val)
                                        if data_type == "steps"
                                        else val,
                                        "id": f"{data_type}-{remote_handle}-{day_str}",
                                    }
                                )
                    except Exception as exc:
                        logger.warning(
                            f"Failed to fetch remote data for {remote_handle}: {exc}"
                        )

        activities.sort(
            key=lambda x: (
                x["time"]
                if isinstance(x["time"], datetime)
                else datetime.now(timezone.utc)
            ),
            reverse=True,
        )
        return activities
