from dataclasses import dataclass

@dataclass
class Subscription:
    name: str
    url: str
    interval: int = 30
    