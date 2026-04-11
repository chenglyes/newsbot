import os
import time
import logging
import schedule
from concurrent.futures import ThreadPoolExecutor
from configs import Subscription, load_yaml_config
from paper import Paper
from fetcher import Fetcher
from llm import LLMClient

class NewsBot:
    def __init__(self) -> None:
        self.config = load_yaml_config("configs/config.yaml")
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

    def process_subscription(self, subscription: Subscription):
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
            ),
        ],
    )
    from dotenv import load_dotenv
    if load_dotenv():
        logging.info("use dotenv")
    try:
        bot = NewsBot()
        bot.run()
    except KeyboardInterrupt:
        logging.info("stop because user interrupt")
    except Exception as e:
        logging.exception(e)
    else:
        bot.shutdown()
