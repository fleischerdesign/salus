import httpx

from salus.services.insight.providers.base import ILlmProvider


class OllamaProvider(ILlmProvider):
    def __init__(self, api_url: str = "http://localhost:11434") -> None:
        self.api_url = api_url

    def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }
        with httpx.Client() as client:
            response = client.post(
                f"{self.api_url.rstrip('/')}/api/chat",
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            try:
                return str(data["message"]["content"])
            except (KeyError, TypeError) as e:
                raise ValueError(f"Malformed response from Ollama: {e}") from e
