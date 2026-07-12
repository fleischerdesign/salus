import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from salus.models.insight import Insight
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.insight.factory import LLMProviderFactory
from salus.services.insight.providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenAiProvider,
)
from salus.services.insight.service import InsightService


class MockLlmProvider:
    def __init__(self, fail: bool = False) -> None:
        self.calls = []
        self.fail = fail

    def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
        if self.fail:
            raise RuntimeError("API Connection failed")
        self.calls.append((prompt, system_instruction, model))
        return "Dynamic generated health advice: sleep more!"


@pytest.fixture
def uow():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield SqlUnitOfWork(session)


class TestLLMProviderFactory:
    def test_creates_ollama_provider(self):
        p = LLMProviderFactory.create_provider("ollama")
        assert isinstance(p, OllamaProvider)
        assert p.api_url == "http://localhost:11434"

    def test_creates_openai_provider(self):
        p = LLMProviderFactory.create_provider("openai", api_key="test-key")
        assert isinstance(p, OpenAiProvider)
        assert p.api_key == "test-key"
        assert p.api_url == "https://api.openai.com/v1"

    def test_creates_anthropic_provider(self):
        p = LLMProviderFactory.create_provider("anthropic", api_key="anthropic-key")
        assert isinstance(p, AnthropicProvider)
        assert p.api_key == "anthropic-key"
        assert p.api_url == "https://api.anthropic.com/v1"

    def test_creates_deepseek_provider_via_openai_adapter(self):
        p = LLMProviderFactory.create_provider("deepseek", api_key="ds-key")
        assert isinstance(p, OpenAiProvider)
        assert p.api_key == "ds-key"
        assert p.api_url == "https://api.deepseek.com"

    def test_creates_openrouter_provider_via_openai_adapter(self):
        p = LLMProviderFactory.create_provider("openrouter", api_key="or-key")
        assert isinstance(p, OpenAiProvider)
        assert p.api_key == "or-key"
        assert p.api_url == "https://openrouter.ai/api/v1"

    def test_raises_on_unknown_provider(self):
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LLMProviderFactory.create_provider("unknown-provider")


class TestInsightService:
    def test_returns_cached_insight_if_exists(self, uow):
        cached = Insight(
            user_id=1,
            query_date="2026-07-01",
            content="Already cached coach insight",
            model_used="test-model",
        )
        with uow:
            uow.insights.add(cached)

        mock_provider = MockLlmProvider()
        service = InsightService(uow=uow, provider=mock_provider, model="test-model")

        res = service.generate_daily_insight(user_id=1, date_str="2026-07-01")
        assert res.id is not None
        assert res.content == "Already cached coach insight"
        assert len(mock_provider.calls) == 0

    def test_calls_provider_and_caches_result_when_uncached(self, uow):
        mock_provider = MockLlmProvider()
        service = InsightService(uow=uow, provider=mock_provider, model="llama3")

        res = service.generate_daily_insight(user_id=42, date_str="2026-07-01")
        assert res.content == "Dynamic generated health advice: sleep more!"
        assert res.model_used == "llama3"
        assert len(mock_provider.calls) == 1

        res_cached = service.generate_daily_insight(user_id=42, date_str="2026-07-01")
        assert res_cached.content == "Dynamic generated health advice: sleep more!"
        assert len(mock_provider.calls) == 1

    def test_handles_api_failure_gracefully_with_fallback(self, uow):
        mock_provider = MockLlmProvider(fail=True)
        service = InsightService(uow=uow, provider=mock_provider, model="gpt-4o")

        res = service.generate_daily_insight(user_id=99, date_str="2026-07-01")
        assert "⚠️" in res.content
        assert "Failed" in res.content or "fehler" in res.content.lower()
        assert res.id is not None


class TestInsightRoutes:
    def _skip_insight_requires_auth(self, client):
        response = client.get("/api/v1/insights", follow_redirects=False)
        assert response.status_code in (401, 403)

    def _skip_insight_no_data_returns_404(self, authenticated_client):
        response = authenticated_client.get("/api/v1/insights?date=2026-07-01")
        assert response.status_code == 404
        assert "No insight found" in response.json()["error"]
