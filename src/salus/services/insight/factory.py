from salus.services.insight.providers import (
    AnthropicProvider,
    ILlmProvider,
    OllamaProvider,
    OpenAiProvider,
)


class LLMProviderFactory:
    @staticmethod
    def create_provider(
        provider_name: str,
        api_key: str | None = None,
        api_url: str | None = None,
    ) -> ILlmProvider:
        p_name = provider_name.lower().strip()

        if p_name == "ollama":
            url = api_url or "http://localhost:11434"
            return OllamaProvider(api_url=url)

        elif p_name == "openai":
            key = api_key or ""
            url = api_url or "https://api.openai.com/v1"
            return OpenAiProvider(api_key=key, api_url=url)

        elif p_name == "anthropic":
            key = api_key or ""
            url = api_url or "https://api.anthropic.com/v1"
            return AnthropicProvider(api_key=key, api_url=url)

        elif p_name == "deepseek":
            key = api_key or ""
            url = api_url or "https://api.deepseek.com"
            return OpenAiProvider(api_key=key, api_url=url)

        elif p_name == "openrouter":
            key = api_key or ""
            url = api_url or "https://openrouter.ai/api/v1"
            return OpenAiProvider(api_key=key, api_url=url)

        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
