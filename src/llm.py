import os
import openai

class LLMClient:
    def __init__(self, model: str, *,
                 api_base: str | None = None, api_key: str | None = None, timeout: float = 60) -> None:
        if not model:
            model = os.getenv("OPENAI_DEFAULT_MODEL", "")
        if not api_base:
            api_base = os.getenv("OPENAI_BASE_URL")
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=timeout,
        )

    def chat(self, messages) -> str | None:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content
    