"""LLM provider interface. Swapping Gemini for OpenAI means writing one new subclass."""
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from app.core.exceptions import LLMError


@dataclass(frozen=True)
class LLMMessage:
    role: Literal["user", "assistant"]
    content: str


class LLM(ABC):
    @abstractmethod
    def stream(self, system: str, messages: list[LLMMessage]) -> Iterator[str]:
        """Yield the answer piece by piece."""

    def complete(self, system: str, messages: list[LLMMessage]) -> str:
        return "".join(self.stream(system, messages))


class GeminiLLM(LLM):
    def __init__(self, api_key: str, model: str) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def stream(self, system: str, messages: list[LLMMessage]) -> Iterator[str]:
        from google.genai import errors, types

        contents = [
            types.Content(role="user" if m.role == "user" else "model", parts=[types.Part(text=m.content)])
            for m in messages
        ]
        config = types.GenerateContentConfig(system_instruction=system, temperature=0.2)
        try:
            for chunk in self._client.models.generate_content_stream(
                model=self._model, contents=contents, config=config
            ):
                if chunk.text:
                    yield chunk.text
        except errors.APIError as exc:
            raise LLMError("The AI provider request failed (check the API key, model name and quota)") from exc
