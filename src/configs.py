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
    max_results: int = 10
    interval: int = 30

@dataclass
class Config:
    thread_num: int | None = None
    llm: LLMConfig = field(default_factory=LLMConfig)
    subscriptions: list[Subscription] = field(default_factory=list[Subscription])
    senders: list[dict] = field(default_factory=list)

def load_yaml_config(path: str) -> Config:
    config = Config()
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        config.thread_num = data["thread_num"]
        config.llm = LLMConfig(**data["llm"])
        config.subscriptions = [Subscription(**subscriptions) for subscriptions in data["subscriptions"]]
        config.senders = [dict(**sender) for sender in data["senders"]]
    return config
    