import httpx

from salus.services.insight.providers.base import ILlmProvider


class AnthropicProvider(ILlmProvider):
    def __init__(
        self, api_key: str, api_url: str = "https://api.anthropic.com/v1"
    ) -> None:
        self.api_key = api_key
        self.api_url = api_url

    def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 4000,
            "system": system_instruction,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        with httpx.Client() as client:
            response = client.post(
                f"{self.api_url.rstrip('/')}/messages",
                json=payload,
                headers=headers,
                timeout=45.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["content"][0]["text"])
