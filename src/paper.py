from dataclasses import dataclass

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
        md = ""
        if self.title_translation:
            md += f"# {self.title_translation}\n\n"
            md += f"> {self.title}\n\n"
        else:
            md += f"# {self.title}\n\n"
        md += f"链接：<{self.link}>\n\n"
        md += f"作者：{self.author}\n\n"
        md += f"发布日期：{self.published}\n\n"
        if self.summary_translation:
            md += f"## 摘要\n\n{self.summary_translation}\n\n"
        md += f"## Summary\n\n{self.summary}\n\n"
        return md
