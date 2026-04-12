import logging
import sqlite3
from pathlib import Path

class Cache:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_papers (
                    id TEXT PRIMARY KEY,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sent_at ON sent_papers(sent_at)")

    def is_sent(self, paper_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sent_papers WHERE id = ?", (paper_id,))
            return cursor.fetchone() is not None

    def mark_sent(self, paper_id: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO sent_papers (id) VALUES (?)", (paper_id,))
            return True
        except sqlite3.IntegrityError:
            return False

    def cleanup(self, days: int = 30):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sent_papers WHERE sent_at < date('now', '-' || ? || ' days')", (days,))
            deleted = cursor.rowcount
            if deleted > 0:
                logging.info(f"cleanup: deleted {deleted} old records (older than {days} days)")
