import os
import logging
import requests
from paper import Paper
from pathlib import Path

class Sender:
    def __init__(self, name: str) -> None:
        self.name = name

    def send(self, paper: Paper):
        try:
            self._send(paper)
        except Exception as e:
            logging.warning(f"sender '{self.name}': fail to send paper '{paper.id}', exception '{e}'")
        else:
            logging.info(f"sender '{self.name}': success to send paper '{paper.id}'")

    def _send(self, paper: Paper):
        pass

def create_sender(name: str, *args, **kwargs) -> Sender:
    if name == "save_to_file":
        return SaveToFileSender(name, *args, **kwargs)
    if name == "server_chan":
        return ServerChanSender(name, *args, **kwargs)
    if name == "telegram_bot":
        return TelegramBotSender(name, *args, **kwargs)
    return Sender(name)

class SaveToFileSender(Sender):
    def __init__(self, name: str, path: str | None = None) -> None:
        super().__init__(name)
        if not path:
            path = "output"
        self.path = Path(path)

    def _send(self, paper: Paper):
        path = self.path / paper.category
        path.mkdir(parents=True, exist_ok=True)

        file_name = paper.id
        file_name = file_name.replace("http://", "")
        file_name = file_name.replace("https://", "")
        import re
        file_name = re.sub(r'[ <>:"/\\|?*]', "-", file_name)
        
        file_path = path / f"{file_name}.md"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(paper.to_markdown())

class ServerChanSender(Sender):
    def __init__(self, name: str, sendkey: str | None = None) -> None:
        super().__init__(name)
        if not sendkey:
            sendkey = os.getenv("SERVERCHAN_SENDKEY")
        if not sendkey:
            logging.warning(f"sender '{name}': sendkey is None, please config 'sendkey' or environmental variable 'SERVERCHAN_SENDKEY'")
        self.sendkey = sendkey

    def _send(self, paper: Paper):
        if not self.sendkey:
            raise RuntimeWarning("no sendkey")
        sendkey = self.sendkey
        if sendkey.startswith('sctp'):
            import re
            match = re.match(r'sctp(\d+)t', sendkey)
            if match:
                uid = match.group(1)
                url = f"https://{uid}.push.ft07.com/send/{sendkey}.send"
            else:
                raise ValueError("invalid sendkey format for sctp")
        else:
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
        if paper.title_translation:
            title = paper.title_translation
        else:
            title = paper.title
        params = {
            "title": title,
            "desp": paper.to_markdown(),
            "tags": paper.category,
        }
        headers = {
            'Content-Type': 'application/json;charset=utf-8'
        }
        response = requests.post(url, json=params, headers=headers)
        result = response.json()
        code = result.get("code", -1)
        if code != 0:
            raise RuntimeWarning(f"return code '{code}', response '{result}'")

class TelegramBotSender(Sender):
    def __init__(self, name: str, bot_token: str | None = None, chat_id: str | None = None) -> None:
        super().__init__(name)
        if not bot_token:
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not bot_token:
            logging.warning(f"sender '{name}': bot_token is None, please config 'bot_token' or environmental variable 'TELEGRAM_BOT_TOKEN'")
        if not chat_id:
            logging.warning(f"sender '{name}': chat_id is None, please config 'chat_id' or environmental variable 'TELEGRAM_CHAT_ID'")
        self.bot_token = bot_token
        self.chat_id = chat_id

    def _send(self, paper: Paper):
        if not self.bot_token or not self.chat_id:
            raise RuntimeWarning("no bot_token or chat_id")
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        title = paper.title_translation if paper.title_translation else paper.title
        text = f"*{title}*\n\n{paper.to_markdown()}"
        params = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        response = requests.post(url, json=params)
        result = response.json()
        if not result.get("ok"):
            raise RuntimeWarning(f"telegrambot error, response '{result}'")
