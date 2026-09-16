class OpenAICompatibleProvider:
    """Optional adapter. It is never required by the core notebooks.

    Works with the real OpenAI API and with any other service exposing an
    OpenAI-compatible /chat/completions endpoint (Groq, NVIDIA NIM, Google AI
    Studio, a local server, etc.) — swapping providers is just a different
    base_url/api_key/model, no code change. See README.md for concrete
    no-credit-card options.
    """

    def __init__(self, api_key, model, base_url=None):
        if not api_key:
            raise ValueError("LLM_API_KEY is required for the optional provider")
        if not model:
            raise ValueError("LLM_MODEL is required for the optional provider")
        from openai import OpenAI
        kwargs = {"api_key": api_key}
        if base_url:
            # Omitted -> defaults to api.openai.com; set it to target Groq,
            # NVIDIA NIM, Gemini's OpenAI-compat endpoint, etc.
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        # temperature=0: keep responses as reproducible as an LLM can be,
        # consistent with the workshop's determinism goal for everything else.
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0)
        return response.choices[0].message.content or ""
