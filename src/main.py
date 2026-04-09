import os
import uuid
import time
import schedule
import feedparser
from concurrent.futures import ThreadPoolExecutor

class Config:
    class LLM:
        def __init__(self, model: str = "", api_base: str = "", api_key: str = "") -> None:
            self.model = model
            self.api_base = api_base
            self.api_key = api_key

    class Subscription:
        def __init__(self, name: str = "unknow", url: str = "", interval: int = 20) -> None:
            self.name = name
            self.url = url
            self.interval = interval

    def __init__(self) -> None:
        self.llm = self.LLM()
        self.subscriptions = list[self.Subscription]()

    def load(self, path: str):
        with open(path, "r", encoding="utf-8") as file:
            from yaml import safe_load
            config = safe_load(file)
            self.llm = self.LLM(**config["llm"])
            self.subscriptions = [self.Subscription(**subscriptions) for subscriptions in config["subscriptions"]]

class NewsBot:
    def __init__(self) -> None:
        self.config = Config()
        self.config.load("configs/config.yaml")
        self.thread_pool = ThreadPoolExecutor(8)
    
    def run(self):
        def thread_job(job, *args, **kwargs):
            self.thread_pool.submit(job, *args, **kwargs)

        def pending_message(title: str, message: str):
            print(f"SEND MESSAGE: '{title}'")

        def process_subscription(subscription: Config.Subscription):
            print(f"PROCESS SUBSCRIPTION: {subscription.name}")
            feed = feedparser.parse(subscription.url)
            if feed.entries:
                path = f"output/{subscription.name}/"
                os.makedirs(path, exist_ok=True)
                for entry in feed.entries[:1]:
                    message = ""
                    message += f"# {entry["title"]}\n\n"
                    message += f"AUTHORS: {entry["author"]}\n\n"
                    message += f"LINK: {entry["link"]}\n\n"
                    message += f"## SUMMARY\n\n{entry["summary"]}\n\n"

                    file_name = path + f"{str(uuid.uuid4())}.md"
                    with open(file_name, "w") as file:
                        file.write(message)
                        print(f"SAVE MESSAGE: {file_name}")
                    
                    thread_job(pending_message, entry["id"], message)

        for subscription in self.config.subscriptions:
            schedule.every(subscription.interval).minutes.do(thread_job, process_subscription, subscription)

        schedule.run_all()

        while True:
            schedule.run_pending()

            try:
                time.sleep(5)
            except KeyboardInterrupt as e:
                break
        
        self.thread_pool.shutdown(cancel_futures=True)

if __name__ == "__main__":
    bot = NewsBot()
    bot.run()
