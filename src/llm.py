import os
import openai
from dataclasses import dataclass

@dataclass
class LLMConfig:
    model: str = ""
    api_base: str | None = None
    api_key: str | None = None
    timeout: float = 60

class LLM:
    def __init__(self, config: LLMConfig = LLMConfig()) -> None:
        if not config.api_key:
            config.api_key = os.getenv("OPENAI_KEY")
        self.config = config
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
        )

    def chat(self, messages) -> str | None:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=False,
        )
        return response.choices[0].message.content
    