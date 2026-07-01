from typing import Protocol, runtime_checkable


@runtime_checkable
class ILlmProvider(Protocol):
    def generate_insight(self, prompt: str, system_instruction: str, model: str) -> str:
        """Sends a prompt to the LLM provider and returns the text response."""
        ...
