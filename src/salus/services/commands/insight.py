from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("generate_insight")
class GenerateInsightHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        from salus.config import settings
        from salus.services.insight.service import InsightService
        from salus.services.insight.factory import LLMProviderFactory

        date_str = payload.get("date")
        provider = LLMProviderFactory.create_provider(
            provider_name=settings.llm_provider,
            api_key=settings.llm_api_key,
            api_url=settings.llm_api_url,
        )
        service = InsightService(uow, provider=provider, model=settings.llm_model)
        insight = service.generate_daily_insight(user.id or "", date_str or "")
        if not insight:
            return CommandResult(status="error", message="Failed to generate insight")
        record: dict[str, Any] = {
            "id": insight.id, "user_id": insight.user_id,
            "query_date": insight.query_date, "content": insight.content,
            "model_used": insight.model_used,
        }
        return CommandResult(status="created", record=record, id=insight.id)  # pyright: ignore[reportAttributeAccessIssue]