class OpenAICompatibleProvider:
    """Optional adapter. It is never required by the core notebooks."""

    def __init__(self, api_key, model, base_url=None):
        if not api_key:
            raise ValueError("LLM_API_KEY is required for the optional provider")
        if not model:
            raise ValueError("LLM_MODEL is required for the optional provider")
        from openai import OpenAI
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0)
        return response.choices[0].message.content or ""
