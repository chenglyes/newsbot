from dataclasses import dataclass
from datetime import datetime

@dataclass
class Paper:
    id: str
    category: str
    published: str
    title: str = ""
    summary: str = ""
    author: str = ""
    link: str | None = None
    label: str | None = None
    title_translation: str | None = None
    summary_translation: str | None = None
    label_translation: str | None = None

    def to_markdown(self) -> str:
        md = f"# {self.title}\n\n"
        md += f"AUTHORS: {self.author}\n\n"
        md += f"LINK: {self.link}\n\n"
        md += f"## SUMMARY\n\n{self.summary}\n\n"
        return md
