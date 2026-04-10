import os
import time
import logging
import schedule
from concurrent.futures import ThreadPoolExecutor
from paper import Paper
from subscription import Subscription
from fetcher import Fetcher
from llm import LLMClient

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
        self.fetcher = Fetcher()
        self.llm = LLMClient(
            model=self.config.llm.model,
            api_base=self.config.llm.api_base,
            api_key=self.config.llm.api_key,
        )

    def process_paper(self, paper: Paper):
        message = paper.to_markdown()
        import re
        file_name = re.sub(r'[<>:"/\\|?*]', "-", paper.id)
        file_path = f"output/{paper.category}/{file_name}.md"
        with open(file_path, "w") as file:
            file.write(message)
        logging.info(f"save to file: {file_path}")

    def process_subscription(self, subscription):
        logging.info(f"process subscription: {subscription.name}")
        path = f"output/{subscription.name}/"
        os.makedirs(path, exist_ok=True)
        papers = self.fetcher.fectch(subscription.name, subscription.url)
        logging.info(f"fetched {len(papers)} papers")
        for paper in papers:
            self.thread_pool.submit(lambda: self.process_paper(paper))
    
    def run(self):
        logging.info(f"running...")
        for subscription in self.config.subscriptions:
            schedule.every(subscription.interval).minutes.do(
                lambda: self.thread_pool.submit(
                    lambda: self.process_subscription(subscription)))
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(5)

    def shutdown(self):
        schedule.clear()
        self.thread_pool.shutdown(cancel_futures=True)

if __name__ == "__main__":
    from datetime import datetime
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s]%(asctime)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f"logs/{datetime.now().strftime("%Y%m%d-%H.%M.%S")}.log",
                encoding="utf-8",
            )
        ],
    )

    from dotenv import load_dotenv
    load_dotenv()

    try:
        bot = NewsBot()
        bot.run()
    except KeyboardInterrupt:
        logging.info("stop because user interrupt")
    except Exception as e:
        logging.exception(e)
    else:
        bot.shutdown()
