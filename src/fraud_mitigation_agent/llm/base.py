"""Structural interface every LLM provider must satisfy.

Not actually imported/enforced anywhere at runtime (FraudAgent just calls
`.complete(...)` duck-typed) — it exists as documentation for anyone adding a
new provider alongside MockLLMProvider and OpenAICompatibleProvider.
"""
from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, prompt: str, system: str | None = None) -> str:
        ...
