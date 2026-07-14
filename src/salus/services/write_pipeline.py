from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session

from salus.models.sync_push_log import SyncPushLog
from salus.models.user import User
from salus.repositories.entity_meta import (
    ENTITY_META_BY_NAME,
    ENTITY_REGISTRY,
    ENTITY_VALIDATORS,
    EntityMeta,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncOperation, SyncResult
from salus.services.command_registry import get_handler
import salus.services.commands  # noqa: F401 — triggers @register decorators

_PK_FIELDS = {"id", "created_at"}
_DEDUP_TTL_HOURS = 24


class WritePipeline:
    def __init__(self, uow: IUnitOfWork, current_user: User) -> None:
        self.uow = uow
        self.user = current_user
        self.session: Session = uow.session

    def process(self, operations: list[SyncOperation]) -> list[SyncResult]:
        results: list[SyncResult] = []
        client_id_map: dict[str, str] = {}

        dedup_cache = self._load_dedup_cache(operations)

        try:
            for op in operations:
                result = self._process_one(op, client_id_map, dedup_cache)
                results.append(result)
        except Exception:
            self.session.rollback()
            raise

        return results

    def _load_dedup_cache(self, operations: list[SyncOperation]) -> dict[str, SyncResult]:
        client_ids = [op.client_id for op in operations if op.client_id]
        if not client_ids:
            return {}

        self.uow.sync_push_logs.cleanup_expired(_DEDUP_TTL_HOURS)

        rows = self.uow.sync_push_logs.find_by_client_ids(client_ids)

        cache: dict[str, SyncResult] = {}
        for row in rows:
            cache[row.client_id] = SyncResult(
                type="create",
                entity=row.entity,
                client_id=row.client_id,
                id=row.record_id,
                status=row.status,
            )
        return cache

    def _process_one(
        self, op: SyncOperation, client_id_map: dict[str, str], dedup_cache: dict[str, SyncResult],
    ) -> SyncResult:
        if op.client_id and op.client_id in dedup_cache:
            return dedup_cache[op.client_id]

        if op.type == "command":
            return self._handle_command(op)

        entity_class = ENTITY_REGISTRY.get(op.entity or "")
        if not entity_class:
            return SyncResult(
                type=op.type, entity=op.entity or "", status="error",
                message=f"Unknown entity: {op.entity}",
            )

        data = op.data or {}
        data = self._resolve_client_ids(data, client_id_map)

        validator = ENTITY_VALIDATORS.get(op.entity or "")
        if validator:
            error = validator(self.session, self.user, data, op)
            if error:
                return SyncResult(
                    type=op.type, entity=op.entity or "", client_id=op.client_id,
                    status="error", message=error,
                )

        if op.type == "create":
            return self._handle_create(op, data, client_id_map)
        elif op.type == "update":
            return self._handle_update(op, data)
        elif op.type == "delete":
            return self._handle_delete(op)
        else:
            return SyncResult(
                type=op.type, entity=op.entity or "", status="error",
                message=f"Unknown operation type: {op.type}",
            )

    def _handle_command(self, op: SyncOperation) -> SyncResult:
        if not op.command:
            return SyncResult(
                type="command", status="error",
                message="command field is required for type='command'",
            )
        handler_cls = get_handler(op.command)
        if not handler_cls:
            return SyncResult(
                type="command", command=op.command, status="error",
                message=f"Unknown command: {op.command}",
            )
        handler = handler_cls()
        result = handler.execute(self.uow, self.user, op.payload or {})
        if op.client_id and result.id:
            self._log_dedup(op.client_id, f"cmd:{op.command}", result.id, result.status)
        return SyncResult(
            type="command",
            command=op.command,
            client_id=op.client_id,
            id=result.id,
            status=result.status,
            record=result.record,
            message=result.message,
        )

    def _inject_user_id(self, meta: EntityMeta, data: dict[str, Any]) -> dict[str, Any]:
        from salus.services._helpers import uid

        strategy = meta.strategy
        owner_field = meta.owner_field or "user_id"

        if strategy in ("user_scoped", "append_only"):
            data[owner_field] = uid(self.user)
        elif strategy == "shared_nullable" and owner_field not in data:
            data[owner_field] = uid(self.user)
        return data

    def _resolve_client_ids(self, data: dict[str, Any], client_id_map: dict[str, str]) -> dict[str, Any]:
        resolved: dict[str, Any] = {}
        for key, value in data.items():
            if key.endswith("_client_id"):
                real_key = key.replace("_client_id", "_id")
                if isinstance(value, str) and value in client_id_map:
                    resolved[real_key] = client_id_map[value]
                else:
                    resolved[real_key] = value
            else:
                resolved[key] = value
        return resolved

    def _serialize(self, obj: Any) -> dict[str, Any]:
        if hasattr(obj, "model_dump"):
            dumped = obj.model_dump()
            for k, v in dumped.items():
                if isinstance(v, datetime):
                    dumped[k] = v.replace(tzinfo=None).isoformat()
            return dumped
        if hasattr(obj, "__dict__"):
            result = {}
            for k, v in obj.__dict__.items():
                if k.startswith("_"):
                    continue
                if isinstance(v, datetime):
                    result[k] = v.replace(tzinfo=None).isoformat()
                elif v is None or isinstance(v, (str, int, float, bool, list, dict)):
                    result[k] = v
            return result
        return {}

    def _log_dedup(self, client_id: str, entity: str, record_id: str, status: str) -> None:
        self.session.add(SyncPushLog(
            client_id=client_id,
            entity=entity,
            record_id=record_id,
            status=status,
        ))

    def _check_ownership(self, instance: Any, meta: EntityMeta | None = None) -> bool:
        from salus.services._helpers import uid

        uid_self = uid(self.user)
        if hasattr(instance, "user_id") and instance.user_id == uid_self:
            return True
        if hasattr(instance, "owner_id") and instance.owner_id == uid_self:
            return True
        if isinstance(instance, User) and instance.id == uid_self:  # pyright: ignore[reportAttributeAccessIssue]
            return True
        if meta and meta.strategy == "relational" and meta.parent_field:
            parent_id = getattr(instance, meta.parent_field, None)
            if parent_id and meta.parent_model:
                parent = self.session.get(meta.parent_model, parent_id)
                if parent:
                    owner_field = meta.parent_owner_field or "user_id"
                    return hasattr(parent, owner_field) and getattr(parent, owner_field) == uid_self
        return False

    def _handle_create(
        self, op: SyncOperation, data: dict[str, Any], client_id_map: dict[str, str],
    ) -> SyncResult:
        entity_class = ENTITY_REGISTRY[op.entity or ""]
        meta = ENTITY_META_BY_NAME[op.entity or ""]
        data = self._inject_user_id(meta, data)

        now = datetime.now(timezone.utc)
        if hasattr(entity_class, "created_at") and "created_at" not in data:
            data["created_at"] = now
        if hasattr(entity_class, "updated_at") and "updated_at" not in data:
            data["updated_at"] = now

        try:
            instance = entity_class.model_validate(data)
        except Exception as e:
            return SyncResult(
                type=op.type, entity=op.entity or "", client_id=op.client_id,
                status="error", message=str(e),
            )

        self.session.add(instance)
        self.session.flush()

        record_id = instance.id  # pyright: ignore[reportAttributeAccessIssue]
        if op.client_id and record_id is not None:
            client_id_map[op.client_id] = record_id
            self._log_dedup(op.client_id, op.entity or "", record_id, "created")

        return SyncResult(
            type=op.type, entity=op.entity or "", client_id=op.client_id,
            id=record_id, status="created", record=self._serialize(instance),
        )

    def _handle_update(self, op: SyncOperation, data: dict[str, Any]) -> SyncResult:
        entity_class = ENTITY_REGISTRY[op.entity or ""]
        meta = ENTITY_META_BY_NAME.get(op.entity or "")
        if op.id is None:
            return SyncResult(
                type=op.type, entity=op.entity or "", status="error",
                message="id is required for update",
            )

        instance = self.session.get(entity_class, op.id)
        if not instance:
            return SyncResult(type=op.type, entity=op.entity or "", id=op.id, status="not_found")

        if not self._check_ownership(instance, meta):
            return SyncResult(type=op.type, entity=op.entity or "", id=op.id, status="forbidden")

        if op.expected_updated_at and hasattr(instance, "updated_at") and instance.updated_at:  # pyright: ignore[reportAttributeAccessIssue]
            expected = datetime.fromisoformat(op.expected_updated_at)
            if instance.updated_at.replace(tzinfo=None) > expected.replace(tzinfo=None):  # pyright: ignore[reportAttributeAccessIssue]
                return SyncResult(
                    type=op.type, entity=op.entity or "", id=op.id,
                    status="conflict", conflict=self._serialize(instance),
                )

        from pydantic import TypeAdapter

        for key, value in data.items():
            if key in _PK_FIELDS:
                continue
            if hasattr(instance, key):
                if key in entity_class.model_fields:
                    field_info = entity_class.model_fields[key]
                    if field_info.annotation is not None:
                        try:
                            value = TypeAdapter(field_info.annotation).validate_python(value)
                        except Exception as e:
                            return SyncResult(
                                type=op.type, entity=op.entity or "", id=op.id,
                                status="error", message=f"Field '{key}' validation failed: {e}",
                            )
                setattr(instance, key, value)

        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now(timezone.utc)  # pyright: ignore[reportAttributeAccessIssue]

        self.session.add(instance)
        self.session.flush()

        if op.client_id and op.id is not None:
            self._log_dedup(op.client_id, op.entity or "", op.id, "updated")

        return SyncResult(
            type=op.type, entity=op.entity or "", id=op.id, status="updated",
            record=self._serialize(instance),
        )

    def _handle_delete(self, op: SyncOperation) -> SyncResult:
        entity_class = ENTITY_REGISTRY[op.entity or ""]
        meta = ENTITY_META_BY_NAME.get(op.entity or "")
        if op.id is None:
            return SyncResult(
                type=op.type, entity=op.entity or "", status="error",
                message="id is required for delete",
            )

        instance = self.session.get(entity_class, op.id)
        if not instance:
            return SyncResult(type=op.type, entity=op.entity or "", id=op.id, status="deleted")

        if not self._check_ownership(instance, meta):
            return SyncResult(type=op.type, entity=op.entity or "", id=op.id, status="forbidden")

        if hasattr(instance, "deleted_at"):
            instance.deleted_at = datetime.now(timezone.utc)
            self.session.add(instance)
        else:
            self.session.delete(instance)
        self.session.flush()

        if op.client_id and op.id is not None:
            self._log_dedup(op.client_id, op.entity or "", op.id, "deleted")

        return SyncResult(type=op.type, entity=op.entity or "", id=op.id, status="deleted")
