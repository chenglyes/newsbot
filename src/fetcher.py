import logging
import feedparser
from paper import Paper

class Fetcher:
    def __init__(self) -> None:
        pass

    def fectch(self, name: str, url: str, *, max_entries: int | None = None, retry: int = 0) -> list[Paper]:
        logging.info(f"fetch url from '{name}'")
        papers = []
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            logging.warning(f"fail to parse url from '{name}', exception: {e}")
        else:
            if feed.entries:
                if not max_entries:
                    max_entries = len(feed.entries)
                for entry in feed.entries[:max_entries]:
                    paper = Paper(
                        category=name,
                        id=str(entry.id),
                        published=str(entry.published),
                        link=str(entry.link),
                        title=str(entry.title),
                        summary=str(entry.summary),
                        author=str(entry.author),
                    )
                    papers.append(paper)
            elif feed.bozo:
                logging.warning(f"fail to parse url from '{name}', message: {feed.bozo_exception}")
        return papers
    