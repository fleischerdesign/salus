import httpx

from salus.services.insight.providers.base import ILlmProvider


class OpenAiProvider(ILlmProvider):
    def __init__(self, api_key: str, api_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.api_url = api_url

    def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        with httpx.Client() as client:
            response = client.post(
                f"{self.api_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])
