import yaml
from dataclasses import dataclass, field

@dataclass
class LLMConfig:
    model: str | None = None
    api_base: str | None = None
    api_key: str | None = None

@dataclass
class Subscription:
    name: str
    url: str
    interval: int = 30

@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    subscriptions: list[Subscription] = field(default_factory=list[Subscription])

def load_yaml_config(path: str) -> Config:
    config = Config()
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        config.llm = LLMConfig(**data["llm"])
        config.subscriptions = [Subscription(**subscriptions) for subscriptions in data["subscriptions"]]
    return config
