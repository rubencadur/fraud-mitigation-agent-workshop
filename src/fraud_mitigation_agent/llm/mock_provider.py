class MockLLMProvider:
    """Offline provider for Colab: deterministic, no network and no API key."""

    def complete(self, prompt: str, system: str | None = None) -> str:
        # Trivial keyword matching instead of a real model: good enough to
        # demonstrate the agent's plumbing (tool calls, trace, decision) end
        # to end without requiring anyone to bring an API key.
        text = (prompt or "").lower()
        if "fraud mitigation agent" in text or "workshop" in text:
            return "El Fraud Mitigation Agent separa herramientas de contexto, scoring determinístico y decisión auditable."
        if "fraude" in text or "fraud" in text:
            return "El flujo combina reglas, señales de comportamiento y similitud vectorial; el resultado final no depende de una respuesta libre del LLM."
        return "MockLLMProvider: respuesta local reproducible para el workshop."
